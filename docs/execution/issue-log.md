# Issue Log (Problem Log)

Single register of defects and problems. Update on discovery; close only after a
verifying test exists or the fix is confirmed in production.

**Severity:** S1 blocking · S2 major · S3 minor · S4 cosmetic
**Status:** Open · In progress · Closed · Deferred

| ID | Date | Severity | Issue | Root cause | Resolution | Status |
| --- | --- | --- | --- | --- | --- | --- |
| ISSUE-001 | 2026-08-23 | S1 | `get_verse_context` crashed — defined at module level with wrong indentation | Indentation error during initial build | Moved into the service class; route tests added | Closed |
| ISSUE-002 | 2026-08-23 | S2 | Test suite repeatedly failed on search/highlight assertions | Wrong literals in test expectations (misspelled Arabic, incorrect expected output) — not app bugs | Rewrote expectations against verified-correct behavior; suite green (recorded in commit message) | Closed |
| ISSUE-003 | 2026-10-06 | S1 | Environment variables not loaded in production | `.env` / `FLASK_ENV` loading path incorrect | Fixed env loading; compose `env_file` verified; `QURAN_*` prefixed override added to factory | Closed |
| ISSUE-004 | 2026-10-06 → 10-07 | S2 | Google Tag Manager / GA4 / Umami not recording hits | Config id missing and CSP blocking external script/connect | Added `GA_MEASUREMENT_ID`, Umami script tag, CSP allowances for `cloud.umami.is` / `gateway.umami.is` | Closed |
| ISSUE-005 | 2026-10-08 | S2 | `tests/test_routes.py::test_static_js_served` fails: requests `/static/js/search.js` but app serves assets from root (`static_url_path=""`) → 404 | Test written for default Flask static path; app overrides it | Decide canonical URL (fix test to `/js/search.js`, or drop `static_url_path` override), add regression coverage | Open |
| ISSUE-006 | 2026-10-08 | S3 | Nginx config fixes required after first deploy (`fix nginx files`) | Proxy config not validated before deploy | Corrected `nginx/conf.d/quran.conf`; added `nginx -t` to pre-deploy checklist in [deployment.md](../technical/deployment.md) | Closed |
| ISSUE-007 | 2026-10-08 | S4 | Generated/monitoring noise committed (`nginx-logs/*.log`, `__pycache__/*.pyc`, editor swap files) | `.gitignore` incomplete | Logged here; extend `.gitignore` (`nginx-logs/`, `__pycache__/`, `*.un~`) and untrack in WP13 | Open |

## Recurring-problem analysis

- **Analytics/config issues (ISSUE-003, -004) recurred across three releases.**
  Preventive action: a config smoke check (assert CSP headers + analytics id present)
  goes into the release checklist — planned in WP13 of [project-plan.md](../planning/project-plan.md).
- **ISSUE-002** shows the risk of writing expected values from memory for Arabic text:
  always derive expectations from the dataset itself (lesson L3 in
  [lessons-learned.md](../closing/lessons-learned.md)).

## Procedure

1. On discovery: create the next `ISSUE-nnn` row with date, severity, description.
2. Investigate root cause before fixing; record it.
3. Fix + add/adjust a test; run the full suite (`pytest`).
4. Update the affected document in `docs/`; set Status = Closed.
5. S1/S2 issues block a release until closed or explicitly deferred by the owner.
