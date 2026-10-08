# Project Plan (Baseline)

Baseline plan for the Quran App. Changes to scope, schedule or resources follow the
change-control procedure in [project-lifecycle.md](../project-lifecycle.md) §Phase 4.
Status values: `Done` · `In progress` · `Planned` · `Deferred`.

**Version:** 1.0 — baseline date 2026-10-08.

---

## 1. Scope

Authoritative scope (product scope, boundaries, deliverables, constraints, assumptions,
accepted exclusions) lives in
**[scope-statement.md](../initiation/scope-statement.md)** — the plan references it;
scope changes follow §9 below. Requirement-level detail:
[requirements.md](requirements.md).

## 2. Objectives & success measures

| Objective | Measure | Target | Actual |
| --- | --- | --- | --- |
| Browse the whole Qur'an | Surahs served from `quran.json` | 114 | 114 ✅ |
| Reliable search | Test suite green | 0 failures | 70/71 pass ⚠ (see §7) |
| Robust to orthography | Normalizer/highlight tests | pass | pass ✅ |
| Production availability | HTTPS site live | yes | yes ✅ |
| Handover-ready knowledge | `docs/` hub complete | index complete | complete ✅ |

## 3. Work breakdown structure (WBS)

| ID | Work package | Depends on | Owner | Status |
| --- | --- | --- | --- | --- |
| WP1 | Data acquisition & repository layer | — | Dev | Done |
| WP2 | Arabic normalizer | WP1 | Dev | Done |
| WP3 | Inverted index + ranking + highlighting | WP2 | Dev | Done |
| WP4 | Test suite (unit + route) | WP2, WP3 | Dev | Done |
| WP5 | Reading UI (index, surah, context, RTL) | WP1 | Dev | Done |
| WP6 | Search routes + templates (keyword, JSON) | WP3 | Dev | Done |
| WP7 | Passage (fuzzy) search | WP3 | Dev | Done |
| WP8 | Config, error pages, security headers | WP5, WP6 | Dev | Done |
| WP9 | Containerization (Dockerfile, compose) | WP8 | Dev | Done |
| WP10 | Reverse proxy + TLS (Nginx, Certbot) | WP9 | Dev | Done |
| WP11 | SEO & analytics | WP10 | Dev | Done |
| WP12 | Documentation hub (Steps 1–2) | all | Dev | In progress |
| WP13 | Hardening: static-path test fix, CI | WP4, WP12 | Dev | Planned |
| WP14 | Second reading (Warsh) wiring | WP1 | — | Deferred |

## 4. Schedule (actual timeline)

| Milestone | Target window | Actual |
| --- | --- | --- |
| M1 Initiation / first commit | 2026-08-23 | 2026-08-23 |
| M2 Core search engine + test suite | 2026-08-23 → 08-27 | 2026-08-23 → 08-27 |
| M3 Reading UI + passage search | 2026-09-01 → 09-07 | 2026-09-05 → 09-07 |
| M4 Containerization | 2026-09-05 → 09-07 | 2026-09-05 → 09-07 |
| M5 Production proxy + TLS + analytics | 2026-10-01 → 10-07 | 2026-10-01 → 10-07 |
| M6 Documentation repository | 2026-10-08 | 2026-10-08 |
| M7 Hardening & CI | next sprint | Planned |

**Critical path:** WP1 → WP2 → WP3 → WP6 → WP8 → WP9 → WP10 → WP11.

## 5. Budget & resources

| Resource | Allocation | Cost |
| --- | --- | --- |
| Developer | 1 person, part-time sprints | internal |
| Runtime | Python 3.13, Flask, Gunicorn, rapidfuzz, pytest | 0 (OSS) |
| Hosting | 1 VPS + domain (`xmpp.linuxjourney.blog`) | existing infra |
| Certificates | Let's Encrypt via Certbot | 0 |
| Analytics | Umami (cloud), GA4 | 0 |
| Database / search service | none required | 0 |

No monetary budget variance: total external spend is domain/hosting already owned.

## 6. Quality plan

- **Definition of done:** code + tests green + affected `docs/` updated + changelog
  entry.
- **Test strategy:** unit tests on tiny deterministic dataset; session-scoped fixture
  over the real dataset for integration; route tests for HTTP behavior —
  details in [testing.md](../technical/testing.md).
- **Review checklist:** requirements traceability, security headers, parameter caps,
  RTL rendering, links in docs resolve.
- **Release gate:** [requirements.md](requirements.md) §5.

## 7. Known variances (plan vs. actual)

| Variance | Impact | Action |
| --- | --- | --- |
| `test_static_js_served` fails (expects `/static/…`, app serves `/static_url_path=""` → `/js/…`) | 1 of 71 tests red | Logged ISSUE-005; fix scheduled in WP13 |
| Analytics config required several post-release fixes (GTM, env loading, Umami) | Schedule slip 2026-10-06 → 10-07 | Preventive: config checklist + regression route test (WP13) |
| Documentation centralized only in Step 1 (2026-10-08) | Knowledge gap until then | Closed by WP12 |

## 8. Communication plan

Maintained separately in **[communication-plan.md](communication-plan.md)**: channels
and cadence (C1–C11), single-source-of-truth rules, escalation path, meeting cadence.
Stakeholder identification: [stakeholder-analysis.md](../initiation/stakeholder-analysis.md).

## 9. Change control

1. Change request: what and why, referencing the affected requirement.
2. Impact analysis: scope / schedule / resources / risk.
3. Approval: project owner.
4. Implementation: code + docs together, logged in
   [changelog.md](../changelog.md).
5. Verification: full test suite + smoke checklist.

Emergency fixes (production outage, security) may be deployed immediately and reported
retrospectively within 24 hours.
