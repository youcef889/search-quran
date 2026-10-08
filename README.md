# Quran App

A bilingual (Arabic / English) **Flask web application** for  searching the Holy Qur'an. It ships with the full Qur'an text and a custom, Dart-style **inverted-index** search engine that is robust to Qur'anic orthography (tashkeel, dagger alif, and other diacritics).

## Features

- **Browse all 114 surahs** with a clean right-to-left (RTL) interface.
- **Read any surah** verse by verse, in `basmala`-style Arabic with full diacritics.
- **Verse context view** — open any verse and see the surrounding 3 verses before and after it.
- **Powerful full-text search** across the entire Qur'an:
  - AND semantics for multi-word queries (every query word must appear).
  - Relevance ranking (exact phrase, phrase position, word proximity, word order).
  - Paginated results (20 per page).
  - **Word-aware highlighting** that projects matches back onto the original text, preserving all diacritics.
- **Arabic normalization** that handles tashkeel, dagger alif (both orthographic variants), tatweel, and bidi control characters.

## Documentation

All project documentation lives in the centralized, Git-versioned repository
**[docs/](docs/README.md)** — organized by lifecycle phase (`initiation/`,
`planning/`, `execution/`, `closing/`) plus subject matter (`technical/`: architecture,
API, search engine, configuration, deployment, testing, data, ADRs) and a cross-cutting
[project lifecycle](docs/project-lifecycle.md). This README only covers the overview
and quick start.

## Tech Stack

- **Python 3.13**
- **Flask 3.1**
- **Gunicorn** (production WSGI server)
- **Jinja2** templates
- **Docker** for containerization

## Project Structure

```
quran_app/
├── app.py              # Flask application factory & entry point
├── config.py           # Environment config + search hard limits
├── requirements.txt    # Python dependencies
├── Dockerfile          # Container definition (Gunicorn on port 4000)
├── data/               # quran.json (active), warsh.json (unused)
├── repositories/       # JSON data access (QuranRepository)
├── routes/             # main (browse), search (keyword / JSON / passage)
├── services/           # normalizer, quran_search, surah_names
├── static/             # css, js, robots.txt, sitemap.xml
├── templates/          # base, index, search, search_passage, error
├── nginx/ certbot/     # Reverse proxy + TLS
├── tests/              # pytest suite
└── docs/               # Central documentation repository
```

Full breakdown: [docs/technical/architecture.md](docs/technical/architecture.md).

## Getting Started

### Local development

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   python app.py
   ```

4. Open [http://localhost:5000](http://localhost:5000) in your browser.

> The development server runs with `debug=True`.

### Production with Gunicorn

```bash
gunicorn --bind 0.0.0.0:4000 app:app
```

### Docker

```bash
docker build -t quran-app .
docker run -p 4000:4000 quran-app
```

The container serves the app on port **4000**.

## Routes

| Route | Description |
| --- | --- |
| `/` | List all 114 surahs |
| `/surah/<surah_id>` | Read a surah; add `?verse=<n>` to show 3 verses of context |
| `/search?q=<query>&page=<n>` | Keyword search (AND), ranked, paginated |
| `/search/json` | Same search as JSON |
| `/search/passage` | Fuzzy passage match (`threshold`, `limit`) |

Full parameter tables and limits: [docs/technical/api.md](docs/technical/api.md).

## Search

An inverted-index engine over the whole Qur'an: Arabic normalization (tashkeel, dagger
alif in both readings, alef/hamza/ta-marbuta variants), AND retrieval, relevance
ranking, and highlighting projected back onto the fully-diacriticized text — plus a
fuzzy passage mode for quotations with typos.

Specification: [docs/technical/search-engine.md](docs/technical/search-engine.md).

## Data

- `data/quran.json` — main dataset: `{ "surah_id": { "verse_id": "text" } }` (114 surahs).
- `data/warsh.json` — a second Qur'an dataset (currently not wired into the app).

Schemas and provenance: [docs/technical/data.md](docs/technical/data.md).

