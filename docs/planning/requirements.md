# Requirements

Status legend: `Implemented` · `Partial` · `Planned`

## 1. Project objective

A bilingual (Arabic / English) web application for reading and searching the Holy Qur'an,
serving fully-diacriticized text with a search engine robust to Qur'anic orthography.

## 2. Functional requirements

### FR-1 — Surah browsing
- FR-1.1 List all 114 surahs on the home page, right-to-left (RTL) layout. — `Implemented`
- FR-1.2 Open any surah and read its verses one by one with full diacritics. — `Implemented`
- FR-1.3 Show Arabic + English surah names. — `Implemented` (`services/surah_names.py`)

### FR-2 — Verse context
- FR-2.1 Request a verse via `?verse=<n>` and see 3 verses before and 3 after. — `Implemented`
- FR-2.2 Out-of-range surah or verse must not error; invalid surah → 404. — `Implemented`

### FR-3 — Keyword search
- FR-3.1 AND semantics: every query word must occur in a matching verse. — `Implemented`
- FR-3.2 Relevance ranking: exact phrase, phrase occurrence, phrase at start, word
  proximity, natural word order. — `Implemented`
- FR-3.3 Pagination, 20 results per page by default, hard cap 100. — `Implemented`
- FR-3.4 Word-aware highlighting projected onto the original diacriticized text. — `Implemented`
- FR-3.5 Query length capped at 200 characters. — `Implemented`
- FR-3.6 JSON variant of search results for programmatic clients. — `Implemented`

### FR-4 — Passage (fuzzy) search
- FR-4.1 Match a pasted verse or fragment tolerant of typos and missing diacritics. — `Implemented`
- FR-4.2 Configurable similarity threshold (0–100, default 65). — `Implemented`
- FR-4.3 Configurable result limit (default 50, max 100). — `Implemented`

### FR-5 — Arabic normalization
- FR-5.1 Strip tashkeel, Qur'anic marks, tatweel and bidi/invisible control characters. — `Implemented`
- FR-5.2 Normalize alef / hamza / ta-marbuta / alef-maqsura / waw- and yeh-hamza variants. — `Implemented`
- FR-5.3 Support both dagger-alif interpretations (`ٰ → ا`, or removed) so retrieval is
  identical under either reading. — `Implemented`

### FR-6 — Errors & localization
- FR-6.1 Custom 400 / 404 / 500 pages with Arabic messages. — `Implemented`
- FR-6.2 Unknown surah id returns 404. — `Implemented`

### FR-7 — SEO & analytics
- FR-7.1 `robots.txt` and `sitemap.xml` for the public domain. — `Implemented`
- FR-7.2 Privacy-respecting analytics (Umami) and optional Google Analytics 4. — `Implemented`

## 3. Non-functional requirements

### NFR-1 — Performance
- NFR-1.1 Search index built **once at startup**, read-only at request time; no per-request
  indexing. — `Implemented`
- NFR-1.2 Candidate retrieval intersects the smallest posting lists first. — `Implemented`
- NFR-1.3 Highlighting computed only for the current result page. — `Implemented`

### NFR-2 — Correctness & safety
- NFR-2.1 All user-supplied parameters clamped to configured hard caps
  (page, per_page, threshold, limit, query length). — `Implemented`
- NFR-2.2 Security headers: `X-Content-Type-Options`, `X-Frame-Options`,
  `Referrer-Policy`, `Content-Security-Policy`. — `Implemented`
- NFR-2.3 Session cookies `HttpOnly` + `SameSite=Lax`. — `Implemented`
- NFR-2.4 Secrets never committed; `.env` is git-ignored. — `Implemented`

### NFR-3 — Reliability & operations
- NFR-3.1 Production runs under Gunicorn with multiple workers. — `Implemented`
- NFR-3.2 Reverse proxy terminates TLS; HTTP→HTTPS handled by Nginx/Certbot. — `Implemented`
- NFR-3.3 Containers restart automatically (`restart: unless-stopped`). — `Implemented`
- NFR-3.4 Structured application logging with configurable level. — `Implemented`

### NFR-4 — Maintainability
- NFR-4.1 Layered layout: routes → services → repositories. — `Implemented`
- NFR-4.2 Automated test suite covering normalization, search, highlighting,
  pagination, passage search and routes. — `Implemented`
- NFR-4.3 Environment-specific configuration via config classes. — `Implemented`

### NFR-5 — Portability
- NFR-5.1 Fully containerized (Docker + docker-compose). — `Implemented`
- NFR-5.2 No external database or search service required. — `Implemented`

### NFR-6 — Accessibility & UX
- NFR-6.1 RTL rendering for Arabic content. — `Implemented`
- NFR-6.2 Bilingual UI (Arabic / English). — `Partial`

## 4. Out of scope (currently)

Authoritative project scope and accepted exclusions:
[scope-statement.md](../initiation/scope-statement.md) §2. Requirement-level exclusions:

- User accounts, bookmarks, reading history.
- Database persistence — all data is in-memory from JSON files.
- Multiple Qur'an readings wired into the app (`data/warsh.json` is present but unused).
- Offline / PWA support.
- Administrative UI.

## 5. Acceptance criteria (release gate)

1. `pytest` passes with no failures.
2. All `Implemented` requirements behave as described on the manual smoke checklist:
   home → surah → verse context → keyword search → passage search → 404 page.
3. Production stack (`docker compose up`) serves HTTPS with valid certificates.
4. Every behavior change has a matching update in `docs/`.

## 6. Traceability

| Requirement | Primary implementation | Tests |
| --- | --- | --- |
| FR-1, FR-2 | `routes/main.py`, `services/quran_search.py:get_surah*` | `tests/test_routes.py` |
| FR-3 | `routes/search.py`, `services/quran_search.py:search` | `test_keyword_search.py`, `test_pagination.py`, `test_highlighting.py` |
| FR-4 | `services/quran_search.py:search_by_passage` | `test_passage_search.py` |
| FR-5 | `services/normalizer.py` | `test_normalizer.py` |
| FR-6 | `app.py:_register_error_handlers` | `test_routes.py` |
| NFR-2 | `app.py:_register_security_headers`, `config.py` | `test_routes.py` |
