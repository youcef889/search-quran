# Scope Statement

**Phase:** Initiation · **Baseline:** 2026-10-08
Scope changes follow the change-control procedure in
[project-plan.md](../planning/project-plan.md) §9. Detailed requirement-level scope
lives in [requirements.md](../planning/requirements.md).

## 1. Product scope (what the deliverable does)

1. **Reading** — list all 114 surahs; read any surah verse by verse in full
   diacritics; open a verse with ±3 verses of context; Arabic + English surah names;
   RTL bilingual layout.
2. **Keyword search** — AND semantics, relevance ranking (exact phrase, occurrence,
   position, proximity, order), pagination, word-aware highlighting projected onto the
   original diacriticized text; JSON variant for programmatic clients.
3. **Passage search** — fuzzy match tolerant of typos and missing diacritics, with
   configurable threshold and limit.
4. **Normalization** — tashkeel, Qur'anic marks, tatweel, bidi controls, alef/hamza/
   ta-marbuta variants, both dagger-alif readings.
5. **Quality & safety** — automated test suite, hard input caps, security headers,
   custom Arabic error pages.
6. **Operations** — Docker image, compose stack (Gunicorn + Nginx), TLS via Certbot,
   structured logging, restart policies.
7. **Discoverability** — sitemap, robots.txt, Umami + GA4 analytics.
8. **Documentation** — centralized, Git-versioned `docs/` repository.

## 2. Project scope boundaries

### In scope
All eight product areas above, for the single production domain
`xmpp.linuxjourney.blog`, one dataset (`data/quran.json`).

### Out of scope (this release)
| Excluded | Reason |
| --- | --- |
| User accounts, bookmarks, history | No persistence layer by design |
| Database / external search service | Unnecessary for a read-only ~6k-verse dataset |
| Mobile apps, PWA/offline | Web only |
| Admin CMS / content editing | Data is versioned in Git |
| Second reading (Warsh) wired in | `data/warsh.json` present, not connected (Deferred WP14) |
| UI beyond Arabic/English | Two languages only |

## 3. Deliverables

| # | Deliverable | Acceptance |
| --- | --- | --- |
| D1 | Flask application (reader, search, errors) | Route tests green, smoke checklist |
| D2 | Search engine + normalizer | Unit tests green |
| D3 | Test suite (71 tests) | `pytest` passes (see variance ISSUE-005) |
| D4 | Containerized production stack | HTTPS live, `nginx -t` clean |
| D5 | SEO & analytics integration | Sitemap served, analytics hits verified |
| D6 | Documentation repository (`docs/`) | Index complete, all links resolve |

## 4. Constraints

- **Technical:** Python 3.13 / Flask 3.x stack; no database; index built in memory at
  startup; Gunicorn worker count bounded by host memory.
- **Resource:** single developer, part-time cadence.
- **Budget:** domain/hosting already owned; all tooling open source.
- **Regulatory/content:** Qur'anic text must never be altered — normalization is
  index-side only; display and highlighting always use the original orthography.
- **Schedule:** production target October 2026.

## 5. Assumptions

1. `data/quran.json` is complete and correctly ordered (114 surahs).
2. Host capacity suffices for expected traffic with 4 Gunicorn workers.
3. Let's Encrypt availability for automated certificates.
4. The owner is available for approvals within each release cycle.

## 6. Exclusions explicitly accepted by the owner

Accounts, database, mobile apps, CMS, Warsh reading, i18n beyond Arabic/English —
accepted as future-release candidates, not defects.

## 7. Acceptance of this scope

Baseline commits (`initiation/*`) are the acceptance record. Any deviation is a change
request: impact analysis → owner approval → implement → verify → log in
[changelog.md](../changelog.md).
