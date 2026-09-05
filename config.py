import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
QURAN_DATA_FILE = DATA_DIR / "quran.json"


class Config:
    """Base configuration shared by all environments."""

    # Application paths
    QURAN_DATA_FILE = QURAN_DATA_FILE

    # Search defaults and hard caps.
    # The client must never be able to drive these beyond the hard limits;
    # caps protect against expensive or nonsensical requests.
    DEFAULT_PAGE = 1
    DEFAULT_PER_PAGE = 20
    MAX_PER_PAGE = 100
    MAX_PAGE = 100000

    DEFAULT_THRESHOLD = 65
    MIN_THRESHOLD = 0
    MAX_THRESHOLD = 100

    DEFAULT_PASSAGE_LIMIT = 50
    MAX_PASSAGE_LIMIT = 100

    MAX_QUERY_LENGTH = 200

    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Logging
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")


class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")


class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get("SECRET_KEY", Config.SECRET_KEY)
    PREFERRED_URL_SCHEME = "https"


def get_config() -> type[Config]:
    env = os.environ.get("FLASK_ENV", "development")
    if env == "production":
        return ProductionConfig
    return DevelopmentConfig


class TestConfig(Config):
    DEBUG = False
    TESTING = True
