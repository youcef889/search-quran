# Search Engine Specification

Implementation: `services/normalizer.py`, `services/quran_search.py`.
Tests: `tests/test_normalizer.py`, `test_keyword_search.py`, `test_highlighting.py`,
`test_pagination.py`, `test_passage_search.py`.

## 1. Normalization (`Normalizer`)

Pure and stateless. Produces a normalized string plus (internally) a character map back
to the original source positions.

### Removed characters

| Range / char | What it is |
| --- | --- |
| U+06D6–U+06ED | Qur'anic annotation signs |
| U+0610–U+061A | Arabic mark signs |
| U+064B–U+065F | Harakat / tashkeel |
| U+0640 | Tatweel (kashida) |
| U+200B–U+200F | Zero-width & bidi marks |
| U+202A–U+202E, U+2066–U+2069 | Bidi embedding/control characters |

Runs of whitespace collapse to a single space; trailing space is trimmed.

### Character folding

| From | To |
| --- | --- |
| `إ أ آ ٱ` | `ا` |
| `ؤ` | `و` |
| `ئ ى` | `ي` |
| `ة` | `ه` |
| `ٰ` (U+0670 dagger alif) | `ا` if `dagger_as_alef=True`, **removed** if `False` |

### Tokenization

- `TOKEN_RE = [\u0621-\u064A\u0670]+` — a token is a run of Arabic letters (plus dagger alif).
- `ARABIC_LETTER_RE` decides whether a token is a real searchable word.
- `query_tokens()` returns unique tokens **in query order** (deduplicated, order preserved).

## 2. Index construction (once, at startup)

**Search index** — one record per verse:

```python
{"surah": "1", "verse": "1", "text": <original>, "normalized": <dagger→alef>,
 "normalized_no_dagger": <dagger removed>}
```

**Inverted index** — `token → set((surah, verse))`, built from **both** normalized
variants, so a verse is retrieved under either dagger-alif interpretation.

## 3. Keyword search

### Candidate retrieval — AND semantics

1. Tokens that have no postings ⇒ empty result immediately.
2. Posting lists sorted by size; intersect smallest first, short-circuiting on empty.

Word order is irrelevant to retrieval; it only affects ranking.

### Ranking (`_rank`)

| Signal | Points |
| --- | --- |
| Verse equals the query phrase (either dagger variant) | +100 |
| Phrase occurs in verse | +40, plus +5 per extra occurrence |
| Verse starts with the phrase | +30 |
| Each matched query word | +10 |
| Word proximity: `max(0, 20 − span)` where `span` = distance between first occurrences | up to +20 |
| Query words appear in natural order | +10 |

**Ordering:** `(-score, int(surah), int(verse))` — deterministic across runs.

### Pagination

`page`, `per_page` clamped to configured caps; `pages = ceil(total / per_page)`;
if `page` exceeds the last page it is clamped into range. Highlighting is computed for
the current page only.

### Highlighting (`_highlight_words`)

1. Locate each query word in the normalized text (checking both dagger variants).
2. Map matches back to **character ranges in the original text**, so tashkeel and
   Qur'anic marks are never altered or split.
3. Enforce whole-word boundaries — a query word is never highlighted inside another word.
4. Merge overlapping ranges, then emit `segments: [{text, match}, …]` covering the
   whole verse.

If nothing matches, the entire verse is returned as a single non-matching segment.

## 4. Passage (fuzzy) search

Used when the input is a quotation that may contain typos or missing diacritics — a
strict AND query would return nothing.

Algorithm:

1. Normalize the query (`dagger_as_alef=True`). Empty ⇒ no results.
2. **Length pre-filter:** keep verses with `len(text) >= max(1, len(query) // 2)`.
   This prevents a very short verse (e.g. 40:1 "حم") from scoring 100 as a contiguous
   substring of a long query.
3. `rapidfuzz.process.extract(query, choices, scorer=fuzz.partial_ratio,
   score_cutoff=threshold, limit=limit)`.
   `partial_ratio` is used because the input is typically shorter than a full verse —
   it finds the best-aligned substring instead of penalizing length mismatch.
4. Sort by score descending; highlight the query's words in each hit.

Returned `score` is rounded to one decimal.

## 5. Known behaviors & trade-offs

- Exact-word retrieval only in keyword search: a typo yields 0 keyword results — by
  design; passage search is the tolerant path.
- Both dagger-alif variants are indexed, so index size roughly doubles the posting
  entries; acceptable for ~6k verses.
- Ranking weights are named class constants (`EXACT_PHRASE_SCORE`, …) so they can be
  tuned in one place.
- The index is rebuilt only on process start: changing `data/quran.json` requires a
  restart (or new gunicorn workers).
