import json
from pathlib import Path


DATA_FILE = Path(__file__).parent.parent / "data" / "quran.json"


class Quran:

    def __init__(self):
        self.data = self._load()
        self.search_index = self._build_search_index()

    # =========================================================
    # DATA
    # =========================================================

    def _load(self):
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
        """
        Create a simplified Arabic representation used only
        for searching.

        Original Quran text is never modified.
        """

        normalized, _ = cls._normalize_with_map(text)

        return normalized

    @staticmethod
    def _normalize_with_map(text, dagger_as_alef=True):
        """
        Build the normalized representation character-by-character
        while recording, for every normalized character (spaces
        included), its exact position in the original string.

        This allows a match found inside the normalized text to
        be projected back onto the untouched original text,
        even though diacritics and pause marks were removed.

        The superscript (dagger) alef is ambiguous: in some words
        it stands for a written alef (e.g. صِرَٰط -> صراط), in
        others it only marks a long vowel that bare orthography
        does not write (e.g. رَحْمَـٰن -> رحمن). The caller can
        therefore choose whether it becomes an alef or is dropped;
        the search index keeps both variants.

        Returns:
            normalized_text
            index_map  (normalized index -> original index)
        """

        text = str(text)

        normalized_chars = []
        index_map = []

        previous_was_space = True

        for position, char in enumerate(text):

            # -------------------------------------------------
            # Characters dropped entirely:
            # pause marks, small diacritics, tashkeel, tatweel,
            # invisible formatting / bidirectional controls
            # -------------------------------------------------

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

            # -------------------------------------------------
            # Superscript alef: alef or dropped
            # -------------------------------------------------

            if char == "\u0670":
                if not dagger_as_alef:
                    continue
                char = "ا"

            # -------------------------------------------------
            # Character replacements
            # -------------------------------------------------

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

            # -------------------------------------------------
            # Collapse whitespace runs into a single space.
            # The space maps to the first whitespace character
            # of the run.
            # -------------------------------------------------

            if char.isspace():

                if previous_was_space:
                    continue

                char = " "
                previous_was_space = True

            else:
                previous_was_space = False

            normalized_chars.append(char)
            index_map.append(position)

        # Strip trailing space (leading is prevented above)

        while normalized_chars and normalized_chars[-1] == " ":
            normalized_chars.pop()
            index_map.pop()

        return "".join(normalized_chars), index_map

    # =========================================================
    # SEARCH INDEX
    # =========================================================

    def _build_search_index(self):

        index = []

        for surah_id, verses in self.data.items():

            for verse_id, text in verses.items():

                index.append({
                    "surah": surah_id,
                    "verse": verse_id,
                    "text": text,
                    "normalized": self.normalize_arabic(text),
                    "normalized_no_dagger": self._normalize_with_map(
                        text,
                        dagger_as_alef=False
                    )[0]
                })

        return index

    # =========================================================
    # HIGHLIGHT
    # =========================================================

    @staticmethod
    def _highlight(text, query, dagger_as_alef=True):
        """
        Find the query inside the normalized text, then use the
        character position map to project the match back onto
        the original text.

        `dagger_as_alef` must match the normalization variant in
        which the query was found (see _normalize_with_map).

        The actual Arabic text remains unchanged.

        Returns:
            before
            match
            after
        """

        normalized_text, index_map = Quran._normalize_with_map(
            text,
            dagger_as_alef=dagger_as_alef
        )
        normalized_query = Quran.normalize_arabic(query)

        position = normalized_text.find(normalized_query)

        if position == -1 or not normalized_query:
            return {
                "before": text,
                "match": "",
                "after": ""
            }

        # -----------------------------------------------------
        # Map the first and last normalized character of the
        # match back to their exact original positions.
        # -----------------------------------------------------

        start = index_map[position]
        end = index_map[position + len(normalized_query) - 1] + 1

        return {
            "before": text[:start],
            "match": text[start:end],
            "after": text[end:]
        }

    # =========================================================
    # SEARCH
    # =========================================================

    def search(self, query, page=1, per_page=20):

        query = self.normalize_arabic(query)

        if not query:
            return {
                "results": [],
                "page": 1,
                "per_page": per_page,
                "total": 0,
                "pages": 0
            }

        matches = []

        query_words = query.split()

        for item in self.search_index:

            text = item["normalized"]

            # -------------------------------------------------
            # No match: try both dagger-alef variants
            # -------------------------------------------------

            if query in text:
                matched_with_dagger_alef = True
            elif query in item["normalized_no_dagger"]:
                matched_with_dagger_alef = False
            else:
                continue

            # -------------------------------------------------
            # Ranking
            # -------------------------------------------------

            score = 0

            # Exact complete phrase
            if text == query:
                score += 100

            # Phrase occurs at the beginning
            if text.startswith(query):
                score += 30

            # Phrase occurs anywhere
            score += 20

            # Count how many times phrase occurs
            occurrences = text.count(query)
            score += occurrences * 5

            # All query words exist
            if all(word in text for word in query_words):
                score += 10

            matches.append({
                "surah": item["surah"],
                "verse": item["verse"],
                "text": item["text"],
                "score": score,
                "matched_with_dagger_alef": matched_with_dagger_alef
            })

        # -----------------------------------------------------
        # Highest score first
        # -----------------------------------------------------

        matches.sort(
            key=lambda result: result["score"],
            reverse=True
        )

        # =====================================================
        # PAGINATION
        # =====================================================

        total = len(matches)

        pages = (
            (total + per_page - 1) // per_page
            if total
            else 0
        )

        # Protect against invalid page numbers
        page = max(1, page)

        if pages:
            page = min(page, pages)

        start = (page - 1) * per_page
        end = start + per_page

        results = matches[start:end]

        # -----------------------------------------------------
        # Highlight data
        # -----------------------------------------------------

        for result in results:
            result["highlight"] = self._highlight(
                result["text"],
                query,
                dagger_as_alef=result["matched_with_dagger_alef"]
            )
            del result["matched_with_dagger_alef"]

        return {
            "results": results,
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": pages
        }
    def get_verse_context(self, surah_id, verse_id, before=3, after=3):
        """
        Return a selected verse together with surrounding verses.

        Example:
            before=3
            after=3

        gives:

            verse - 3
            verse - 2
            verse - 1
            verse
            verse + 1
            verse + 2
            verse + 3
        """

        surah = self.get_surah(surah_id)

        if not surah:
            return []

        verse_numbers = sorted(
            int(number)
            for number in surah.keys()
        )

        verse_number = int(verse_id)

        if verse_number not in verse_numbers:
            return []

        selected_index = verse_numbers.index(verse_number)

        start = max(
            0,
            selected_index - before
        )

        end = min(
            len(verse_numbers),
            selected_index + after + 1
        )

        context = []

        for number in verse_numbers[start:end]:

            context.append({
                "number": number,
                "text": surah[str(number)],
                "selected": number == verse_number
            })

        return context
