# Architecture

## 1. System overview

```
                 ┌─────────────────────────────────────────────┐
   Browser ────► │ Nginx (80/443, TLS, reverse proxy, logs)    │
                 └──────────────────┬──────────────────────────┘
                                    │ proxy_pass http://quran-app:4000
                 ┌──────────────────▼──────────────────────────┐
                 │ Gunicorn (4 workers) ── Flask app (app.py)  │
                 │   routes/  →  services/  →  repositories/   │
                 └──────────────────┬──────────────────────────┘
                                    │ read once at startup
                 ┌──────────────────▼──────────────────────────┐
                 │ data/quran.json  (in-memory, read-only)     │
                 └─────────────────────────────────────────────┘
```

Both containers share the `quran` bridge network. Certbot certificates are mounted
read-only into Nginx.

## 2. Layers

| Layer | Location | Responsibility |
| --- | --- | --- |
| Presentation | `templates/`, `static/` | RTL HTML, CSS, client-side search JS, SEO files |
| HTTP | `routes/main.py`, `routes/search.py` | Parameter parsing/clamping, calling services, rendering |
| Application | `services/quran_search.py`, `services/normalizer.py`, `services/surah_names.py` | Indexing, retrieval, ranking, highlighting, fuzzy matching |
| Data access | `repositories/quran_repository.py` | Load and expose the JSON dataset |
| Configuration | `config.py` | Environment-specific settings and hard limits |
| Composition root | `app.py` | `create_app()` factory: logging, extensions, blueprints, errors, security headers |

**Dependency direction:** routes → services → repositories. Nothing flows backwards.

## 3. Application lifecycle

1. `create_app()` builds config from `FLASK_ENV` (`DevelopmentConfig` / `ProductionConfig`),
   then overlays any `QURAN_*` variables (`app.config.from_prefixed_env("QURAN")`).
2. `_init_extensions()` loads `data/quran.json` into `QuranRepository` and constructs
   `QuranSearchService`, which builds:
   - `search_index` — one normalized record per verse (~6k verses),
   - `inverted_index` — `word → set((surah, verse))`, indexed under **both**
     dagger-alif variants.
3. The repository and service are stored in `app.extensions` and shared across requests.
   They are immutable after construction, so they are safe under concurrent workers.
4. Blueprints `main` and `search` are registered, error handlers and security headers
   attached, and `surah_names` is injected into every template context.

## 4. Request flow (keyword search)

```
GET /search?q=...&page=2&per_page=20
  → routes/search.py:_query_param / _int_param   (truncate to 200 chars, clamp)
  → QuranSearchService.search()
      normalize query → query tokens (unique, order preserved)
      → _candidate_ids(): intersect posting lists, smallest first   [AND]
      → _rank() each candidate
      → sort by (-score, surah, verse)
      → clamp pagination, slice the requested page
      → _highlight_words() only for that page
  → render templates/search.html
```

## 5. Request flow (passage search)

```
GET /search/passage?q=...&threshold=65&limit=50
  → clamp threshold (0–100), limit (1–100)
  → QuranSearchService.search_by_passage()
      normalize query
      length pre-filter: drop verses shorter than len(query)/2
      rapidfuzz process.extract(..., scorer=partial_ratio, score_cutoff=threshold)
      → sort by score desc, highlight each hit
  → render templates/search_passage.html
```

## 6. Project layout

```
quran_app/
├── app.py                  # Application factory, error handlers, security headers
├── config.py               # Config / Development / Production / Test classes
├── requirements.txt
├── Dockerfile              # python:3.13-slim, gunicorn on :4000
├── docker-compose.yml      # web + nginx, network `quran`
├── data/                   # quran.json (active), warsh.json (unused)
├── repositories/           # QuranRepository — JSON data access
├── routes/                 # main (browse), search (keyword/passage/JSON)
├── services/               # normalizer, quran_search, surah_names
├── templates/              # base, index, search, search_passage, error
├── static/                 # css, js, robots.txt, sitemap.xml
├── nginx/conf.d/           # proxy config; nginx-logs/ volume target
├── certbot/                # letsencrypt conf + www challenge volume
├── tests/                  # pytest suite
└── docs/                   # ← this repository
```

## 7. Key design decisions

| Decision | Rationale |
| --- | --- |
| In-memory index built at startup | Dataset is small and read-only; removes per-request file I/O and any external search dependency |
| Two dagger-alif normalizations indexed | Retrieval is correct whether U+0670 is read as alif or dropped |
| AND semantics for keyword search | Multi-word queries are intended as "all of these"; fuzzy fallback exists as passage search |
| Layered modules + app factory | Testable (`create_app(TestConfig)`), replaceable data source, clear ownership |
| No database | Nothing to persist; state is fully derived from JSON |

See [decisions.md](decisions.md) for the ADR trail.
