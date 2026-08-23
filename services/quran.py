import json
import re
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

    @staticmethod
    def normalize_arabic(text):
        """
        Create a simplified Arabic representation used only
        for searching.

        Original Quran text is never modified.
        """

        text = str(text)

        # Remove Quranic annotation / pause marks
        text = re.sub(
            r"[\u06D6-\u06ED]",
            "",
            text
        )

        # Remove tashkeel
        text = re.sub(
            r"[\u0610-\u061A\u064B-\u065F\u0670]",
            "",
            text
        )

        # Normalize Alef variants
        text = re.sub(
            r"[إأآٱ]",
            "ا",
            text
        )

        # Normalize Hamza
        text = text.replace("ؤ", "و")
        text = text.replace("ئ", "ي")

        # Normalize Alef Maqsura
        text = text.replace("ى", "ي")

        # Normalize Ta Marbuta
        text = text.replace("ة", "ه")

        # Remove Tatweel
        text = text.replace("ـ", "")

        # Normalize whitespace
        text = re.sub(r"\s+", " ", text)

        return text.strip()

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
                    "normalized": self.normalize_arabic(text)
                })

        return index

    # =========================================================
    # HIGHLIGHT
    # =========================================================

    @staticmethod
    def _highlight(text, query):
        """
        Find the query inside the original text.

        The actual Arabic text remains unchanged.

        Returns:
            before
            match
            after
        """

        normalized_text = Quran.normalize_arabic(text)
        normalized_query = Quran.normalize_arabic(query)

        position = normalized_text.find(normalized_query)

        if position == -1:
            return {
                "before": text,
                "match": "",
                "after": ""
            }

        # -----------------------------------------------------
        # Because normalization can change the number of
        # characters, we cannot safely use the normalized
        # position directly against the original string.
        #
        # For now, return the original text and let the UI
        # display the complete verse.
        # -----------------------------------------------------

        return {
            "before": "",
            "match": text,
            "after": ""
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
            # No match
            # -------------------------------------------------

            if query not in text:
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
                "score": score
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
                query
            )

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
