import re

# Arabic letters used to decide whether a normalized token is a real
# searchable word (i.e. contains at least one Arabic letter).
ARABIC_LETTER_RE = re.compile(r"[\u0621-\u064A]")
# A searchable word is a run of Arabic letters, including the dagger alif.
TOKEN_RE = re.compile(r"[\u0621-\u064A\u0670]+")


class Normalizer:
    """Normalization and tokenization of Qur'anic Arabic.

    This is a pure, stateless helper. The normalization preserves the two
    Qur'anic dagger-alif variants so that search behaves identically whether
    a dagger alif (U+0670) is treated as an alif or removed.
    """

    def normalize(self, text: str, dagger_as_alef: bool = True) -> str:
        """Return normalized Arabic without the character-position map."""
        normalized, _ = self._normalize_with_map(text, dagger_as_alef)
        return normalized

    def tokenize(self, text: str, dagger_as_alef: bool = True) -> list[str]:
        """Return the searchable words extracted from normalized text."""
        normalized = self.normalize(text, dagger_as_alef)
        return TOKEN_RE.findall(normalized)

    def query_tokens(self, query: str) -> list[str]:
        """Return unique normalized query words, preserving query order."""
        words = self.tokenize(query, dagger_as_alef=True)
        result = []
        seen = set()
        for word in words:
            if word and word not in seen:
                seen.add(word)
                result.append(word)
        return result

    @staticmethod
    def _normalize_with_map(text: str, dagger_as_alef: bool = True) -> tuple[str, list[int]]:
        """Normalize Arabic while mapping each normalized character back to
        its position in the untouched source text.

        Two variants are supported because dagger alif (U+0670) can behave
        differently in Qur'anic orthography:

        - dagger_as_alef=True:  ٰ -> ا
        - dagger_as_alef=False: ٰ is removed
        """
        text = str(text)

        normalized_chars = []
        index_map = []
        previous_was_space = True

        for position, char in enumerate(text):
            # Qur'anic marks, tashkeel, tatweel and bidi controls are removed.
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
