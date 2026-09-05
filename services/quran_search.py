from collections import defaultdict
import re

from rapidfuzz import fuzz, process

from repositories.quran_repository import QuranRepository
from services.normalizer import ARABIC_LETTER_RE, TOKEN_RE, Normalizer


class QuranSearchService:
    """In-memory search over the Qur'an.

    Indexes are built once at construction time and are read-only
    afterwards, so the service is safe to share across concurrent Flask
    requests. No request mutates shared state.
    """

    # Ranking weights. Named constants keep the scoring strategy readable
    # and easy to tune without scattering magic numbers through the code.
    EXACT_PHRASE_SCORE = 100
    PHRASE_OCCURRENCE_SCORE = 40
    EXTRA_PHRASE_OCCURRENCE_SCORE = 5
    PHRASE_AT_START_SCORE = 30
    PER_MATCHED_WORD_SCORE = 10
    DISTANCE_CLOSEST_BONUS = 20
    NATURAL_ORDER_SCORE = 10

    def __init__(
        self,
        repository: QuranRepository,
        normalizer: Normalizer | None = None,
    ) -> None:
        self._repo = repository
        self._normalizer = normalizer or Normalizer()

        self.search_index = self._build_search_index()
        self.inverted_index = self._build_inverted_index()

        # Cached lookups used by fuzzy passage matching. Built once here so
        # they are not recomputed on every request.
        self._passage_choices: dict[tuple[str, str], str] = {
            (item["surah"], item["verse"]): item["normalized"]
            for item in self.search_index
        }
        self._by_verse_id: dict[tuple[str, str], dict] = {
            (item["surah"], item["verse"]): item
            for item in self.search_index
        }

    # ------------------------------------------------------------------
    # Index construction
    # ------------------------------------------------------------------

    def _build_search_index(self) -> list[dict]:
        """Build one compact, normalized record per verse."""
        index = []
        for surah_id, verses in self._repo.get_surahs().items():
            for verse_id, text in verses.items():
                normalized = self._normalizer.normalize(text, True)
                normalized_no_dagger = self._normalizer.normalize(text, False)
                index.append({
                    "surah": str(surah_id),
                    "verse": str(verse_id),
                    "text": text,
                    "normalized": normalized,
                    "normalized_no_dagger": normalized_no_dagger,
                })
        return index

    def _build_inverted_index(self) -> dict[str, set[tuple[str, str]]]:
        """Build ``normalized_word -> set((surah, verse))``.

        Both dagger-alif variants are indexed so a search retrieves a verse
        regardless of which orthographic interpretation a word needs.
        """
        index: dict[str, set[tuple[str, str]]] = defaultdict(set)
        for item in self.search_index:
            verse_id = (item["surah"], item["verse"])
            for normalized_text in (item["normalized"], item["normalized_no_dagger"]):
                for token in TOKEN_RE.findall(normalized_text):
                    if ARABIC_LETTER_RE.search(token):
                        index[token].add(verse_id)
        return dict(index)

    # ------------------------------------------------------------------
    # Candidate retrieval (AND semantics)
    # ------------------------------------------------------------------

    def _candidate_ids(self, query_words: list[str]) -> set[tuple[str, str]]:
        """Return verses containing every query word (AND).

        Word order is irrelevant. The smallest posting lists are
        intersected first for efficiency.
        """
        if not query_words:
            return set()

        posting_lists = []
        for word in query_words:
            postings = self.inverted_index.get(word)
            if not postings:
                return set()
            posting_lists.append(postings)

        posting_lists.sort(key=len)
        candidates = set(posting_lists[0])
        for postings in posting_lists[1:]:
            candidates.intersection_update(postings)
            if not candidates:
                break
        return candidates

    # ------------------------------------------------------------------
    # Keyword search
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        """Search verses that contain all query words (AND semantics)."""
        normalized_query = self._normalizer.normalize(query, True)
        query_words = self._normalizer.query_tokens(query)

        if not normalized_query or not query_words:
            return self._empty_results(page, per_page)

        candidate_ids = self._candidate_ids(query_words)
        if not candidate_ids:
            return self._empty_results(page, per_page)

        matches = [
            self._rank(self._by_verse_id[verse_id], query_words, normalized_query)
            for verse_id in candidate_ids
        ]

        # Deterministic ordering: relevance first, then surah/verse.
        matches.sort(
            key=lambda result: (
                -result["score"],
                int(result["surah"]),
                int(result["verse"]),
            )
        )

        total = len(matches)
        page, per_page = self._clamp_pagination(page, per_page, total)
        pages = self._pages(total, per_page)

        start = (page - 1) * per_page
        results = matches[start : start + per_page]

        # Highlight only the current page to avoid wasted work.
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

    def _rank(
        self,
        item: dict,
        query_words: list[str],
        normalized_query: str,
    ) -> dict:
        """Score a verse against the query and produce a result record."""
        text = item["normalized"]
        text_no_dagger = item["normalized_no_dagger"]

        score = 0

        # Exact complete phrase is the strongest match.
        if text == normalized_query or text_no_dagger == normalized_query:
            score += self.EXACT_PHRASE_SCORE

        # Exact phrase in the verse, regardless of word order elsewhere.
        phrase_occurrences = max(
            text.count(normalized_query),
            text_no_dagger.count(normalized_query),
        )
        if phrase_occurrences:
            score += self.PHRASE_OCCURRENCE_SCORE
            score += phrase_occurrences * self.EXTRA_PHRASE_OCCURRENCE_SCORE

        # Phrase at the beginning gets an additional bonus.
        if text.startswith(normalized_query) or text_no_dagger.startswith(normalized_query):
            score += self.PHRASE_AT_START_SCORE

        # Every query word is guaranteed present by candidate retrieval.
        score += len(query_words) * self.PER_MATCHED_WORD_SCORE

        # Prefer verses where the words sit closer together. This ranks
        # natural multi-word phrases higher without requiring their order.
        positions = self._first_occurrence_positions(item, query_words)
        if len(positions) == len(query_words):
            span = max(positions) - min(positions)
            score += max(0, self.DISTANCE_CLOSEST_BONUS - span)
            if positions == sorted(positions):
                score += self.NATURAL_ORDER_SCORE

        return {
            "surah": item["surah"],
            "verse": item["verse"],
            "text": item["text"],
            "score": score,
        }

    @staticmethod
    def _first_occurrence_positions(
        item: dict,
        query_words: list[str],
    ) -> list[int]:
        """Return the first token position of each query word, using either
        dagger-alif variant as a fallback. Missing words are skipped."""
        tokens = TOKEN_RE.findall(item["normalized"])
        tokens_no_dagger = TOKEN_RE.findall(item["normalized_no_dagger"])

        positions = []
        for word in query_words:
            if word in tokens:
                positions.append(tokens.index(word))
            elif word in tokens_no_dagger:
                positions.append(tokens_no_dagger.index(word))
        return positions

    # ------------------------------------------------------------------
    # Fuzzy passage search
    # ------------------------------------------------------------------

    def search_by_passage(
        self,
        query: str,
        threshold: int = 65,
        limit: int = 50,
    ) -> dict:
        """Match a user-entered verse or fragment against the Qur'an,
        tolerant of typos, missing diacritics and partial input.

        This does not require every word to match exactly (a single typo
        would otherwise make AND-based retrieval return nothing). Instead the
        whole normalized input is compared against every verse with a fuzzy
        scorer.

        ``fuzz.partial_ratio`` is used because the input may be a chunk of a
        verse (shorter than the full verse); it finds the best-aligned
        substring match rather than penalizing a length mismatch.

        A length pre-filter excludes verses that are much shorter than the
        query. ``partial_ratio`` treats the longer string as the haystack, so
        a short stored verse (e.g. 40:1 "حم") that happens to be a contiguous
        substring of the query scores 100 even though it is irrelevant; a
        genuine match for a long query is never dramatically shorter than the
        query itself.
        """
        normalized_query = self._normalizer.normalize(query, True)
        if not normalized_query:
            return {"results": [], "total": 0}

        min_length = max(1, len(normalized_query) // 2)
        choices = {
            verse_id: text
            for verse_id, text in self._passage_choices.items()
            if len(text) >= min_length
        }
        if not choices:
            return {"results": [], "total": 0}

        raw_matches = process.extract(
            normalized_query,
            choices,
            scorer=fuzz.partial_ratio,
            score_cutoff=threshold,
            limit=limit,
        )

        query_words = TOKEN_RE.findall(normalized_query)

        results = []
        for _, score, verse_id in raw_matches:
            item = self._by_verse_id[verse_id]
            results.append({
                "surah": item["surah"],
                "verse": item["verse"],
                "text": item["text"],
                "score": round(score, 1),
                # Shows which of the user's words matched cleanly, which is
                # useful feedback when the input may contain mistakes.
                "highlight": self._highlight_words(item["text"], query_words),
            })

        results.sort(key=lambda result: -result["score"])
        return {"results": results, "total": len(results)}

    # ------------------------------------------------------------------
    # Highlighting
    # ------------------------------------------------------------------

    def _highlight_words(
        self,
        text: str,
        query_words: list[str],
    ) -> dict:
        """Build highlight segments by projecting normalized matches back
        onto the original stored text.

        Matches are located in normalized text and mapped to the source so
        that tashkeel and Qur'anic marks are preserved and never touched.
        Both dagger-alif variants are checked per word. Word boundaries are
        enforced so a query word is never highlighted inside another word.
        """
        empty_highlight = {
            "before": text,
            "match": "",
            "after": "",
            "segments": [{"text": text, "match": False}],
        }

        if not query_words:
            return empty_highlight

        ranges = []
        for word in query_words:
            if not word:
                continue
            ranges.extend(self._word_ranges(text, word))

        if not ranges:
            return empty_highlight

        # Merge overlapping ranges (including the same word found through
        # both dagger-alif variants).
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
                segments.append({"text": text[cursor:start], "match": False})
            segments.append({"text": text[start:end], "match": True})
            cursor = end

        if cursor < len(text):
            segments.append({"text": text[cursor:], "match": False})

        return {
            "before": text,
            "match": "",
            "after": "",
            "segments": segments,
        }

    def _word_ranges(self, text: str, word: str) -> list[tuple[int, int]]:
        """Return source-text char ranges where ``word`` occurs as a whole
        word, checking both dagger-alif variants."""
        ranges = []
        for dagger_as_alef in (True, False):
            normalized_text, index_map = self._normalizer._normalize_with_map(
                text,
                dagger_as_alef=dagger_as_alef,
            )
            normalized_word = self._normalizer.normalize(word, dagger_as_alef)
            if not normalized_word:
                continue

            # Word-aware matching. Boundaries prevent a query such as "دين"
            # from matching inside "الدين".
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
                ranges.append((index_map[start_pos], index_map[end_pos] + 1))
        return ranges

    # ------------------------------------------------------------------
    # Surah / verse access (delegated to the repository)
    # ------------------------------------------------------------------

    def get_surahs(self) -> dict[str, dict[str, str]]:
        """Return all surahs keyed by surah id."""
        return self._repo.get_surahs()

    def get_surah(self, surah_id: int | str) -> dict[str, str]:
        """Return the verses of a surah keyed by verse number."""
        return self._repo.get_surah(surah_id)

    def get_verse(self, surah_id: int | str, verse_id: int | str) -> str | None:
        """Return the stored text of a single verse, or None if absent."""
        return self._repo.get_verse(surah_id, verse_id)

    # ------------------------------------------------------------------
    # Verse context
    # ------------------------------------------------------------------

    def get_verse_context(
        self,
        surah_id: int | str,
        verse_id: int | str,
        before: int = 3,
        after: int = 3,
    ) -> list[dict]:
        """Return a window of verses around a given verse within its surah."""
        surah = self._repo.get_surah(surah_id)
        if not surah:
            return []

        verse_numbers = sorted(int(number) for number in surah)
        verse_number = int(verse_id)
        if verse_number not in verse_numbers:
            return []

        selected_index = verse_numbers.index(verse_number)
        start = max(0, selected_index - before)
        end = min(len(verse_numbers), selected_index + after + 1)

        return [
            {
                "number": number,
                "text": surah[str(number)],
                "selected": number == verse_number,
            }
            for number in verse_numbers[start:end]
        ]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _clamp_pagination(
        page: int,
        per_page: int,
        total: int,
    ) -> tuple[int, int]:
        page = max(1, page)
        per_page = max(1, per_page)
        pages = QuranSearchService._pages(total, per_page)
        if pages:
            page = min(page, pages)
        return page, per_page

    @staticmethod
    def _pages(total: int, per_page: int) -> int:
        return (total + per_page - 1) // per_page if total else 0

    @staticmethod
    def _empty_results(page: int, per_page: int) -> dict:
        return {
            "results": [],
            "page": 1,
            "per_page": per_page,
            "total": 0,
            "pages": 0,
        }
