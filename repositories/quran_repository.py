import json
from pathlib import Path


class QuranRepository:
    """Loads and provides read-only access to the Qur'an data.

    The repository exposes the authoritative stored text exactly as it
    appears in ``quran.json``. No normalization is applied here; that is a
    search-service concern.
    """

    def __init__(self, data_file: Path) -> None:
        self._data = self._load(data_file)

    @staticmethod
    def _load(data_file: Path) -> dict[str, dict[str, str]]:
        if not data_file.exists():
            raise FileNotFoundError(f"Qur'an data not found: {data_file}")
        with open(data_file, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def get_surahs(self) -> dict[str, dict[str, str]]:
        """Return all surahs keyed by surah id."""
        return self._data

    def get_surah(self, surah_id: int | str) -> dict[str, str]:
        """Return the verses of a surah keyed by verse number."""
        return self._data.get(str(surah_id), {})

    def get_verse(self, surah_id: int | str, verse_id: int | str) -> str | None:
        """Return the stored text of a single verse, or None if absent."""
        return self.get_surah(surah_id).get(str(verse_id))
