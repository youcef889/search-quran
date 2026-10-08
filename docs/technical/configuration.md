# Configuration

Source of truth: `config.py`. Secrets live in `.env` (git-ignored) and are never
documented with values here.

## Selection

```python
get_config()  # FLASK_ENV == "production" → ProductionConfig, else DevelopmentConfig
```

The factory then overlays any `QURAN_*` environment variables:

```python
app.config.from_prefixed_env("QURAN")   # e.g. QURAN_SECRET_KEY=... → config["SECRET_KEY"]
```

So `QURAN_*` variables take precedence over class defaults.

## Classes

| Class | When | Notable settings |
| --- | --- | --- |
| `Config` | Base for all | limits, `SECRET_KEY`, cookies, `GA_MEASUREMENT_ID`, `LOG_LEVEL` |
| `DevelopmentConfig` | `FLASK_ENV` unset/other | `DEBUG=True`, `LOG_LEVEL=DEBUG` (unless `LOG_LEVEL` set) |
| `ProductionConfig` | `FLASK_ENV=production` | `DEBUG=False`, `PREFERRED_URL_SCHEME=https` |
| `TestConfig` | tests | `DEBUG=False`, `TESTING=True` |

## Settings reference

### Application

| Name | Default | Notes |
| --- | --- | --- |
| `QURAN_DATA_FILE` | `data/quran.json` | Absolute path resolved from the repo root |
| `SECRET_KEY` | `dev-secret-change-me` | **Must** be set via env in production |
| `SESSION_COOKIE_HTTPONLY` | `True` | |
| `SESSION_COOKIE_SAMESITE` | `Lax` | |
| `LOG_LEVEL` | `INFO` (`DEBUG` in dev) | Read by `_configure_logging` |
| `GA_MEASUREMENT_ID` | unset | Google Analytics 4; optional |
| `PREFERRED_URL_SCHEME` | `https` (production only) | |

### Search limits (hard caps — clients cannot exceed them)

| Name | Default | Min | Max |
| --- | --- | --- | --- |
| `DEFAULT_PAGE` | 1 | 1 | — |
| `DEFAULT_PER_PAGE` | 20 | 1 | `MAX_PER_PAGE` |
| `MAX_PER_PAGE` | 100 | | |
| `MAX_PAGE` | 100000 | | |
| `DEFAULT_THRESHOLD` | 65 | `MIN_THRESHOLD` (0) | `MAX_THRESHOLD` (100) |
| `DEFAULT_PASSAGE_LIMIT` | 50 | 1 | `MAX_PASSAGE_LIMIT` (100) |
| `MAX_QUERY_LENGTH` | 200 | | queries are truncated, not rejected |

## Environment variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `FLASK_ENV` | Prod: yes | `production` selects `ProductionConfig` |
| `SECRET_KEY` | Prod: yes | Flask signing key |
| `LOG_LEVEL` | No | `DEBUG` / `INFO` / `WARNING` / … |
| `GA_MEASUREMENT_ID` | No | Enables GA4 measurement id in templates |
| `QURAN_*` | No | Any prefixed var overrides the matching config key |

`.env` is loaded by `docker-compose.yml` (`env_file: .env`) for the `web` service and is
listed in `.gitignore`.

## Security headers (`app.py`)

Applied to every response via `setdefault` (never overriding an existing header):

| Header | Value |
| --- | --- |
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `Referrer-Policy` | `no-referrer` |
| `Content-Security-Policy` | `default-src 'self'`; allows Google Fonts styles/fonts, Umami script, Umami connect endpoints |
