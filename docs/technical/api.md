# API Reference

Base URL (production): `https://xmpp.linuxjourney.blog`
All responses are UTF-8; JSON responses use `ensure_ascii = False`.

## Parameter limits

Enforced server-side by `config.py` — client input is never trusted beyond these caps.

| Parameter | Default | Min | Max |
| --- | --- | --- | --- |
| `q` | `""` | — | 200 chars (truncated) |
| `page` | 1 | 1 | 100000 |
| `per_page` | 20 | 1 | 100 |
| `threshold` | 65 | 0 | 100 |
| `limit` | 50 | 1 | 100 |

Invalid or non-numeric values fall back to the default; numeric values are clamped
into range (never an error).

---

## `GET /`

Surah list.

**Template:** `index.html`
**Response:** HTML — all 114 surahs with Arabic and English names.

---

## `GET /surah/<surah_id>`

Read a surah.

| Param | Type | Description |
| --- | --- | --- |
| `surah_id` | path int | 1–114; unknown id → **404** |
| `verse` | query int | Optional. Shows 3 verses before and 3 after this verse, with the requested verse marked as selected |

**Response:** HTML (`index.html`). Without `verse`, all verses of the surah are returned.

---

## `GET /search`

Keyword search (AND semantics, relevance ranked, paginated).

| Param | Description |
| --- | --- |
| `q` | Query words; every word must appear in a matching verse |
| `page` | Page number |
| `per_page` | Page size |

**Template:** `search.html`
**Response:** HTML with highlighted matches.

### Result record (service level)

```json
{
  "surah": "1",
  "verse": "1",
  "text": "بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ",
  "score": 180,
  "highlight": {
    "before": "...",
    "match": "",
    "after": "",
    "segments": [{"text": "…", "match": false}, {"text": "…", "match": true}]
  }
}
```

`segments` is a partition of `text`: contiguous chunks flagged `match: true/false`.
Concatenating all `segment.text` reproduces the original verse exactly.

---

## `GET /search/json`

Same query parameters and same result structure as `GET /search`, returned as JSON.

**Response:** `application/json`

```json
{
  "results": [ { "surah": "1", "verse": "1", "text": "…", "score": 180, "highlight": { … } } ],
  "page": 1,
  "per_page": 20,
  "total": 123,
  "pages": 7
}
```

Ordering: `-score`, then numeric surah, then numeric verse (deterministic).

---

## `GET /search/passage`

Fuzzy passage match — tolerant of typos, missing diacritics and partial input.

| Param | Description |
| --- | --- |
| `q` | A verse, fragment or (possibly mistyped) quotation |
| `threshold` | Minimum similarity 0–100 (default 65) |
| `limit` | Maximum results (default 50, max 100) |

**Template:** `search_passage.html`
**Response:** HTML.

**Response shape (service level):**

```json
{
  "results": [
    { "surah": "1", "verse": "1", "text": "…", "score": 93.5, "highlight": { … } }
  ],
  "total": 12
}
```

`score` is a `rapidfuzz.fuzz.partial_ratio` value rounded to one decimal.

---

## `GET /robots.txt`, `GET /sitemap.xml`

Served as static files from `static/` (SEO; sitemap lists `/`, `/search`,
`/search/passage`).

## `GET /static/…`

CSS/JS assets. `static_url_path=""`, so assets are served from the root
(e.g. `/css/style.css`).

---

## Error responses

Custom HTML error pages (Arabic messages) from `templates/error.html`:

| Code | Meaning |
| --- | --- |
| 400 | Bad request |
| 404 | Page or surah not found |
| 500 | Unhandled server error (exception logged) |
