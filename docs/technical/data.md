# Data

## Datasets

| File | Status | Contents |
| --- | --- | --- |
| `data/quran.json` | **Active** — the only dataset wired into the app | Full Qur'an text, 114 surahs |
| `data/warsh.json` | Present but **unused** | A second Qur'an dataset (Warsh-style), not referenced by any code path |

## Schema (`quran.json`)

```json
{
  "1": {
    "1": "بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ",
    "2": "ٱلْحَمْدُ لِلَّهِ رَبِّ ٱلْعَـٰلَمِينَ"
  },
  "2": { "1": "إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ" }
}
```

- Keys are **strings**: outer = surah id (`"1"`–`"114"`), inner = verse id.
- Values are the verse text with **full diacritics (tashkeel)** and Qur'anic marks —
  stored exactly as read; normalization happens at index time, never in the data file.
- Loaded by `repositories/quran_repository.py:_load`, which reads the file once and
  returns `dict[str, dict[str, str]]`.

## Access layer

`QuranRepository` is the only reader of the JSON file:

| Method | Returns |
| --- | --- |
| `get_surahs()` | `{surah_id: {verse_id: text}}` |
| `get_surah(surah_id)` | `{verse_id: text}` or empty dict |
| `get_verse(surah_id, verse_id)` | verse text or `None` |

Constructed once at startup (`app.py:_init_extensions`) from `config["QURAN_DATA_FILE"]`
and treated as read-only afterwards.

## Derived data (built at startup, not stored on disk)

| Structure | Shape | Purpose |
| --- | --- | --- |
| `search_index` | list of `{surah, verse, text, normalized, normalized_no_dagger}` | One record per verse |
| `inverted_index` | `word → set((surah, verse))` | AND candidate retrieval, both dagger variants |
| `_passage_choices` | `(surah, verse) → normalized text` | Fuzzy passage matching candidates |

## Rules

1. **Never edit verse text in place** to "normalize" it — highlighting and display depend
   on the original orthography.
2. Adding/changing a dataset requires a **restart** (indexes are built once per process).
3. Any new data file must be listed in this document and its schema documented.
4. Large datasets must stay out of Git unless they are part of the shipped product;
   `data/` is currently committed intentionally (no database, image needs the file).
