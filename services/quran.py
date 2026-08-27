import json
import re
from pathlib import Path
from collections import defaultdict


DATA_FILE = Path(__file__).parent.parent / "data" / "quran.json"


class Quran:
    """Qur'an data access and Dart-style inverted-index search."""

    # Arabic letters used by the Dart search index to decide whether a
    # normalized token is a real searchable word.
    ARABIC_LETTER_RE = re.compile(r"[\u0621-\u064A]")
    TOKEN_RE = re.compile(r"[\u0621-\u064A\u0670]+")

    def __init__(self):
        self.data = self._load()
        self.search_index = self._build_search_index()
        self.inverted_index = self._build_inverted_index()

    # =========================================================
    # DATA
    # =========================================================

    def _load(self):
        if not DATA_FILE.exists():
            raise FileNotFoundError(
                f"Qur'an data not found: {DATA_FILE}"
            )

        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    def get_surahs(self):
        return self.data

    def get_surah(self, surah_id):
        return self.data.get(str(surah_id), {})

    # =========================================================
    # ARABIC NORMALIZATION
    # =========================================================

    @classmethod
    def normalize_arabic(cls, text):
        normalized, _ = cls._normalize_with_map(text)
        return normalized

    @staticmethod
    def _normalize_with_map(text, dagger_as_alef=True):
        """
        Normalize Arabic while keeping a map from every normalized
        character to its position in the untouched source text.

        Two variants are supported because dagger alif (U+0670) can
        behave differently in Qur'anic orthography:

        - dagger_as_alef=True:  ٰ -> ا
        - dagger_as_alef=False: ٰ is removed
        """
        text = str(text)

        normalized_chars = []
        index_map = []
        previous_was_space = True

        for position, char in enumerate(text):
            # Qur'anic marks, tashkeel, tatweel and bidi controls.
            if (
                "\u06D6" <= char <= "\u06ED"
                or "\u0610" <= char <= "\u061A"
                or "\u064B" <= char <= "\u065F"
                or char == "\u0640"
                or "\u200B" <= char <= "\u200F"
                or "\u202A" <= char <= "\u202E"
                or "\u2066" <= char <= "\u2069"
            ):
                continue

            if char == "\u0670":
                if not dagger_as_alef:
                    continue
                char = "ا"
            elif char in "إأآٱ":
                char = "ا"
            elif char == "ؤ":
                char = "و"
            elif char == "ئ":
                char = "ي"
            elif char == "ى":
                char = "ي"
            elif char == "ة":
                char = "ه"

            if char.isspace():
                if previous_was_space:
                    continue
                char = " "
                previous_was_space = True
            else:
                previous_was_space = False

            normalized_chars.append(char)
            index_map.append(position)

        while normalized_chars and normalized_chars[-1] == " ":
            normalized_chars.pop()
            index_map.pop()

        return "".join(normalized_chars), index_map

    @classmethod
    def tokenize(cls, text, dagger_as_alef=True):
        """Tokenize normalized Arabic into searchable words."""
        normalized = cls._normalize_with_map(
            text,
            dagger_as_alef=dagger_as_alef,
        )[0]
        return cls.TOKEN_RE.findall(normalized)

    @classmethod
    def _query_tokens(cls, query):
        """
        Return unique normalized query words while preserving query order.
        """
        words = cls.tokenize(query, dagger_as_alef=True)
        result = []
        seen = set()

        for word in words:
            if word and word not in seen:
                seen.add(word)
                result.append(word)

        return result

    # =========================================================
    # SEARCH INDEX
    # =========================================================

    def _build_search_index(self):
        """
        Keep one compact record per verse.  The actual candidate retrieval
        is performed by inverted_index below.
        """
        index = []

        for surah_id, verses in self.data.items():
            for verse_id, text in verses.items():
                normalized, _ = self._normalize_with_map(text, True)
                normalized_no_dagger, _ = self._normalize_with_map(
                    text,
                    dagger_as_alef=False,
                )

                index.append({
                    "surah": str(surah_id),
                    "verse": str(verse_id),
                    "text": text,
                    "normalized": normalized,
                    "normalized_no_dagger": normalized_no_dagger,
                })

        return index

    def _build_inverted_index(self):
        """
        Build the same fundamental structure as the Dart generator:

            normalized_word -> set(verse_id)

        Python uses a tuple (surah, verse) as the verse ID because it avoids
        assumptions about the numeric encoding used by the Flutter app.

        Both dagger-alif normalization variants are indexed, so a search can
        retrieve a verse regardless of which orthographic interpretation is
        needed for a particular word.
        """
        index = defaultdict(set)

        for item in self.search_index:
            verse_id = (item["surah"], item["verse"])

            variants = (
                item["normalized"],
                item["normalized_no_dagger"],
            )

            for normalized_text in variants:
                for token in self.TOKEN_RE.findall(normalized_text):
                    if self.ARABIC_LETTER_RE.search(token):
                        index[token].add(verse_id)

        return dict(index)

    # =========================================================
    # MATCHING / RANKING
    # =========================================================

    @staticmethod
    def _count_phrase(text, phrase):
        if not phrase:
            return 0
        return text.count(phrase)

    @staticmethod
    def _contains_word(tokens, word):
        return word in tokens

    def _candidate_ids(self, query_words):
        """
        Retrieve candidates using AND semantics, exactly the behavior wanted
        from the Dart inverted index for multi-word queries.

        Every query word must exist in the verse. Word order is irrelevant.
        """
        if not query_words:
            return set()

        posting_lists = []
        for word in query_words:
            postings = self.inverted_index.get(word)
            if not postings:
                return set()
            posting_lists.append(postings)

        # Intersect the smallest posting lists first for efficiency.
        posting_lists.sort(key=len)
        candidates = set(posting_lists[0])

        for postings in posting_lists[1:]:
            candidates.intersection_update(postings)
            if not candidates:
                break

        return candidates

    # =========================================================
    # HIGHLIGHTING
    # =========================================================

    @classmethod
    def _highlight_words(cls, text, query_words):
        """
        Highlight every matching query word independently.

        This is deliberately not a simple substring replacement. Matches are
        located in normalized text and projected back to the original Qur'an
        text, preserving tashkeel and Qur'anic marks.

        Both dagger-alif variants are checked per word.
        """
        if not query_words:
            return {
                "before": text,
                "match": "",
                "after": "",
                "segments": [{"text": text, "match": False}],
            }

        ranges = []

        for word in query_words:
            if not word:
                continue

            for dagger_as_alef in (True, False):
                normalized_text, index_map = cls._normalize_with_map(
                    text,
                    dagger_as_alef=dagger_as_alef,
                )
                normalized_word = cls._normalize_with_map(
                    word,
                    dagger_as_alef=dagger_as_alef,
                )[0]

                if not normalized_word:
                    continue

                # Word-aware matching. Since normalized text contains Arabic
                # words separated by spaces, checking boundaries prevents a
                # query such as "دين" from matching inside "الدين".
                pattern = re.compile(
                    r"(?<![\u0621-\u064A])"
                    + re.escape(normalized_word)
                    + r"(?![\u0621-\u064A])"
                )

                for found in pattern.finditer(normalized_text):
                    start_pos = found.start()
                    end_pos = found.end() - 1

                    if start_pos >= len(index_map) or end_pos >= len(index_map):
                        continue

                    start = index_map[start_pos]
                    end = index_map[end_pos] + 1
                    ranges.append((start, end))

        if not ranges:
            return {
                "before": text,
                "match": "",
                "after": "",
                "segments": [{"text": text, "match": False}],
            }

        # Merge overlapping ranges, including the case where the same word
        # was found through both dagger-alif variants.
        ranges.sort()
        merged = []
        for start, end in ranges:
            if not merged or start > merged[-1][1]:
                merged.append([start, end])
            else:
                merged[-1][1] = max(merged[-1][1], end)

        segments = []
        cursor = 0
        for start, end in merged:
            if cursor < start:
                segments.append({
                    "text": text[cursor:start],
                    "match": False,
                })
            segments.append({
                "text": text[start:end],
                "match": True,
            })
            cursor = end

        if cursor < len(text):
            segments.append({
                "text": text[cursor:],
                "match": False,
            })

        return {
            "before": text,
            "match": "",
            "after": "",
            "segments": segments,
        }

    # Backwards-compatible single-query helper.
    @classmethod
    def _highlight(cls, text, query, dagger_as_alef=True):
        query_words = cls._query_tokens(query)
        return cls._highlight_words(text, query_words)

    # =========================================================
    # SEARCH
    # =========================================================

    def search(self, query, page=1, per_page=20):
        normalized_query = self.normalize_arabic(query)
        query_words = self._query_tokens(query)

        if not normalized_query or not query_words:
            return {
                "results": [],
                "page": 1,
                "per_page": per_page,
                "total": 0,
                "pages": 0,
            }

        # -----------------------------------------------------
        # 1. Candidate retrieval: AND over query words.
        # -----------------------------------------------------
        candidate_ids = self._candidate_ids(query_words)

        if not candidate_ids:
            return {
                "results": [],
                "page": 1,
                "per_page": per_page,
                "total": 0,
                "pages": 0,
            }

        by_id = {
            (item["surah"], item["verse"]): item
            for item in self.search_index
        }

        matches = []

        for verse_id in candidate_ids:
            item = by_id[verse_id]
            text = item["normalized"]
            text_no_dagger = item["normalized_no_dagger"]

            tokens = self.TOKEN_RE.findall(text)
            tokens_no_dagger = self.TOKEN_RE.findall(text_no_dagger)

            # -------------------------------------------------
            # 2. Ranking. AND matching is mandatory; these are
            #    relevance bonuses only.
            # -------------------------------------------------
            score = 0

            # Exact complete phrase is the strongest match.
            if text == normalized_query or text_no_dagger == normalized_query:
                score += 100

            # Exact phrase in the verse, regardless of word order elsewhere.
            phrase_occurrences = max(
                self._count_phrase(text, normalized_query),
                self._count_phrase(text_no_dagger, normalized_query),
            )
            if phrase_occurrences:
                score += 40
                score += phrase_occurrences * 5

            # Phrase at the beginning gets an additional bonus.
            if (
                text.startswith(normalized_query)
                or text_no_dagger.startswith(normalized_query)
            ):
                score += 30

            # All words are already guaranteed by candidate retrieval.
            score += len(query_words) * 10

            # Prefer verses where the words occur fewer positions apart.
            # This makes natural multi-word queries rank better without
            # requiring their original order.
            positions = []
            for word in query_words:
                try:
                    positions.append(tokens.index(word))
                except ValueError:
                    try:
                        positions.append(tokens_no_dagger.index(word))
                    except ValueError:
                        pass

            if len(positions) == len(query_words):
                span = max(positions) - min(positions)
                score += max(0, 20 - span)

                if positions == sorted(positions):
                    score += 10

            matches.append({
                "surah": item["surah"],
                "verse": item["verse"],
                "text": item["text"],
                "score": score,
            })

        # Deterministic ordering: relevance, then surah/verse.
        matches.sort(
            key=lambda result: (
                -result["score"],
                int(result["surah"]),
                int(result["verse"]),
            )
        )

        # -----------------------------------------------------
        # 3. Pagination.
        # -----------------------------------------------------
        total = len(matches)
        pages = (total + per_page - 1) // per_page if total else 0

        try:
            page = int(page)
        except (TypeError, ValueError):
            page = 1

        page = max(1, page)
        if pages:
            page = min(page, pages)

        start = (page - 1) * per_page
        end = start + per_page
        results = matches[start:end]

        # -----------------------------------------------------
        # 4. Highlight every query word independently.
        # -----------------------------------------------------
        for result in results:
            result["highlight"] = self._highlight_words(
                result["text"],
                query_words,
            )

        return {
            "results": results,
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": pages,
        }

    # =========================================================
    # VERSE CONTEXT
    # =========================================================

    def get_verse_context(self, surah_id, verse_id, before=3, after=3):
        surah = self.get_surah(surah_id)

        if not surah:
            return []

        verse_numbers = sorted(int(number) for number in surah.keys())
        verse_number = int(verse_id)

        if verse_number not in verse_numbers:
            return []

        selected_index = verse_numbers.index(verse_number)
        start = max(0, selected_index - before)
        end = min(len(verse_numbers), selected_index + after + 1)

        context = []
        for number in verse_numbers[start:end]:
            context.append({
                "number": number,
                "text": surah[str(number)],
                "selected": number == verse_number,
            })

        return context
