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
├── requirements.txt    # Python dependencies
├── Dockerfile          # Container definition (Gunicorn on port 4000)
├── data/
│   ├── quran.json      # Primary Qur'an text (surah -> verse -> text)
│   └── warsh.json      # Additional Warsh-style Qur'an dataset
├── routes/
│   ├── __init__.py
│   └── main.py         # Route definitions (index, surah, search)
├── services/
│   ├── __init__.py
│   └── quran.py        # Quran data access + inverted-index search engine
├── static/
├── templates/
│   ├── base.html       # RTL base layout with header + search bar
│   ├── index.html      # Surah list / surah reader
│   └── search.html     # Search results page
```

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
| `/surah/<surah_id>` | Read a surah; add `?verse=<n>` to show context around a verse |
| `/search?q=<query>&page=<n>` | Search the Qur'an, with pagination |

## Search

The search engine (`services/quran.py`) mirrors a Dart-style inverted index found in a companion Flutter application. Key behaviors:

- **Normalization** — removes Qur'anic marks and short vowels, normalizes alef/hamza/ta-marbuta variants, and supports both dagger-alif interpretations (`ٰ -> ا` or removed).
- **Candidate retrieval** — intersects the smallest posting lists first for efficiency.
- **Ranking** — bonuses for exact full-phrase match, phrase occurrence, phrase at verse start, word proximity, and in-order words.
- **Highlighting** — every query word is highlighted independently; matches are found in normalized text and mapped back to positions in the original, fully-diacriticized verse.

## Data

- `data/quran.json` — main dataset: `{ "surah_id": { "verse_id": "text" } }` (114 surahs).
- `data/warsh.json` — a second Qur'an dataset (currently not wired into the app).


