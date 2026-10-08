# Testing

## Running

```bash
pytest                                  # whole suite
pytest tests/test_normalizer.py         # one module
pytest -k highlight                     # by name
pytest -q                               # quiet
```

`pytest` is pinned in `requirements.txt` — no extra install step.

## Layout

| File | Covers |
| --- | --- |
| `tests/conftest.py` | Fixtures and the synthetic dataset |
| `tests/test_normalizer.py` | Arabic normalization, dagger alif, tokenization |
| `tests/test_keyword_search.py` | AND semantics, ranking, empty/edge queries |
| `tests/test_highlighting.py` | Match projection onto original diacriticized text |
| `tests/test_pagination.py` | Page/per_page clamping, page counts |
| `tests/test_passage_search.py` | Fuzzy matching, threshold and limit |
| `tests/test_routes.py` | HTTP status codes, templates, security headers, 404 |

## Fixtures (`conftest.py`)

| Fixture | Scope | Provides |
| --- | --- | --- |
| `service` | session | `QuranSearchService` over the **real** `data/quran.json` |
| `tiny_repository` | function | `QuranRepository` over a 2-surah synthetic Qur'an written to `tmp_path` |
| `tiny_service` | function | Search service over the tiny dataset |
| `app` | session | Flask app built with `TestConfig` |
| `client` | session | `app.test_client()` |

### `TINY_QURAN`

A two-surah, five-verse dataset using real Qur'anic orthography (tashkeel, dagger alif,
alef variants) so normalization, ranking and highlighting are exercised realistically
while staying deterministic and fast. Unit tests prefer `tiny_service`; tests that need
realistic scale use `service`.

## Conventions

- Tests are pure — no network, no writes outside `tmp_path`.
- Assert behavior (statuses, ordering, segment integrity), not implementation details.
- A new requirement needs a test; see the traceability table in
  [requirements.md](../planning/requirements.md).

## Adding a test

1. Pick the module matching the layer (`normalizer`, search service, route).
2. Reuse an existing fixture; add a new one to `conftest.py` only if shared.
3. Keep the tiny dataset in `conftest.py` — extend it rather than creating new
   ad-hoc datasets.
4. Run the full suite before committing.
