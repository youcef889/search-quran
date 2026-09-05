import json
from pathlib import Path

import pytest

from repositories.quran_repository import QuranRepository
from services.quran_search import QuranSearchService

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "quran.json"

# Small synthetic Qur'an for deterministic unit tests. Uses real Qur'anic
# orthography (tashkeel, dagger alif, alif variants) so normalization,
# ranking and highlighting behavior is exercised realistically.
TINY_QURAN = {
    "1": {
        "1": "بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ",
        "2": "ٱلْحَمْدُ لِلَّهِ رَبِّ ٱلْعَـٰلَمِينَ",
        "3": "مَـٰلِكِ يَوْمِ ٱلدِّينِ",
    },
    "2": {
        "1": "إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ",
        "2": "ٱهْدِنَا ٱلصِّرَٰطَ ٱلْمُسْتَقِيمَ",
    },
}


@pytest.fixture(scope="session")
def service():
    """Search service built over the real quran.json dataset."""
    return QuranSearchService(QuranRepository(DATA_FILE))


@pytest.fixture
def tiny_repository(tmp_path):
    data_file = tmp_path / "quran.json"
    data_file.write_text(json.dumps(TINY_QURAN, ensure_ascii=False), encoding="utf-8")
    return QuranRepository(data_file)


@pytest.fixture
def tiny_service(tiny_repository):
    return QuranSearchService(tiny_repository)


@pytest.fixture(scope="session")
def app():
    from app import create_app
    from config import TestConfig

    return create_app(TestConfig)


@pytest.fixture(scope="session")
def client(app):
    return app.test_client()