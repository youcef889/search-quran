# Project Lifecycle — Phases & Procedure

This document is the detailed account of how the Quran App project is initiated,
planned, executed, monitored and controlled, and closed. It maps the generic project
management process onto this project's real timeline and defines the procedure to be
followed for any future release.

**Governing artifacts:** [project-plan.md](planning/project-plan.md),
[issue-log.md](execution/issue-log.md), [risk-management-plan.md](planning/risk-management-plan.md),
[lessons-learned.md](closing/lessons-learned.md),
[requirements.md](planning/requirements.md), [decisions.md](technical/decisions.md),
[changelog.md](changelog.md).

```
Initiation ──► Planning ──► Execution ──► Monitoring & Controlling ──► Closing
   ▲               ▲              │               │                    │
   └───────────────┴──────────────┴───────────────┴────────────────────┘
                    change control / lessons learned feedback
```

Monitoring & Controlling runs **in parallel** with Execution, not after it.

## Documentation organization (phases × subjects)

The repository in `docs/` arranges every artifact by the lifecycle phase it belongs to,
with cross-phase subject matter kept separately:

| Folder | Phase / subject | Artifacts |
| --- | --- | --- |
| [initiation/](initiation/project-charter.md) | Phase 1 — Initiation | project charter, scope statement, stakeholder analysis |
| [planning/](planning/project-plan.md) | Phase 2 — Planning | project plan, requirements, risk management plan, communication plan |
| [execution/](execution/status-report.md) | Phases 3–4 — Execution & Monitoring/Control | status reports, progress updates, meeting minutes, issue log |
| [closing/](closing/final-project-report.md) | Phase 5 — Closing | final project report, lessons learned, closing documentation |
| [technical/](technical/architecture.md) | Subject matter (all phases) | architecture, API, search engine, configuration, deployment, testing, data, ADRs |

Rule of thumb: **if it is about a phase, it lives in that phase's folder; if it is
about the product, it lives in `technical/`.**

---

## Phase 1 — Initiation

**Documents (`docs/initiation/`):** [project-charter.md](initiation/project-charter.md), [scope-statement.md](initiation/scope-statement.md), [stakeholder-analysis.md](initiation/stakeholder-analysis.md)


**Purpose:** Obtain formal approval that the project is worth doing and define it at a
high level.

### Procedure

1. Identify the business need: a fast, accurate, ad-free way to read and search the Holy
   Qur'an in Arabic and English on the web.
2. Draft the **project charter** (below) — goals, scope boundaries, stakeholders,
   success criteria, authority to proceed.
3. Confirm feasibility: static dataset, no database, no third-party services required
   beyond hosting ⇒ low technical risk.
4. Get stakeholder sign-off. Sign-off is recorded by committing the charter to Git —
   the commit is the approval record.

### Deliverable — Project charter

| Field | Content |
| --- | --- |
| **Project name** | Quran App — bilingual Qur'an reader & search engine |
| **Problem statement** | Existing readers offer weak search that breaks on Qur'anic orthography (tashkeel, dagger alif, alef variants) |
| **Objective** | Deliver a web app that browses all 114 surahs and searches the full text robustly, diacritics preserved |
| **Scope (in)** | Reading, verse context, keyword search, fuzzy passage search, Arabic normalization, RTL bilingual UI, Dockerized HTTPS deployment, automated tests |
| **Scope (out)** | User accounts, database, mobile apps, admin CMS, multiple readings (Warsh unused) |
| **Stakeholders** | Project owner (sponsor), development team, end users (Arabic/English readers), hosting/ops |
| **Success criteria** | All 114 surahs browsable; multi-word search returns correct ranked results; full test suite green; site live over HTTPS |
| **Budget / resources** | 1 developer, open-source stack, single host + domain; no paid services except domain/hosting |
| **Milestones** | See schedule in [project-plan.md](planning/project-plan.md) |
| **Authority** | Owner approves scope changes; all changes recorded via change control |

### Entry / exit criteria

- **Entry:** business need identified.
- **Exit:** charter approved and committed ⇒ project authorized.

### This project's record

Initiation: **2026-08-23** — first commit (`Quran search application`).

---

## Phase 2 — Planning

**Documents (`docs/planning/`):** [project-plan.md](planning/project-plan.md), [requirements.md](planning/requirements.md), [risk-management-plan.md](planning/risk-management-plan.md), [communication-plan.md](planning/communication-plan.md)


**Purpose:** Turn the charter into an executable plan: detailed requirements, design,
schedule, budget, quality and risk plans.

### Procedure

1. **Requirements engineering** — elicit, analyze, document and baseline functional and
   non-functional requirements with acceptance criteria
   → [requirements.md](planning/requirements.md). Requirements are the reference for every later
   change request.
2. **Technical design** — choose stack, define layers, data flow, index strategy
   → [architecture.md](technical/architecture.md), [search-engine.md](technical/search-engine.md).
   Significant choices are recorded as ADRs → [decisions.md](technical/decisions.md).
3. **Work breakdown** — decompose into work packages: data layer, normalizer, search
   engine, routes/templates, tests, containerization, reverse proxy/TLS, SEO/analytics,
   documentation.
4. **Schedule** — sequence packages with dependencies (index before routes; app before
   proxy) → timeline table in [project-plan.md](planning/project-plan.md).
5. **Quality plan** — definition of done, test strategy, review checklist
   → [testing.md](technical/testing.md).
6. **Risk plan** — identify, assess, prioritize, assign mitigations
   → [risk-management-plan.md](planning/risk-management-plan.md).
7. **Communication plan** — who is informed, how often, through what channel (Git
   commits/PRs are the primary record).
8. **Baselining** — the plan is committed to `docs/`; from then on, deviations follow
   the change-control procedure below.

### Deliverables

Project plan, schedule, requirements baseline, architecture/design, test strategy,
risk register, communication plan — all living in `docs/`.

### Entry / exit criteria

- **Entry:** charter approved.
- **Exit:** plan reviewed, baselined and committed; work packages are actionable.

### This project's record

Planning: **2026-08-23 → 2026-08-27** — dataset and inverted-index design, AND-search
semantics, test fixtures (`TINY_QURAN`), Dockerfile and dependency pinning
(2026-09-05), README baseline.

---

## Phase 3 — Execution

**Documents (`docs/execution/`):** [progress-updates.md](execution/progress-updates.md), [issue-log.md](execution/issue-log.md)


**Purpose:** Perform the work packages, assign resources, produce deliverables, keep
stakeholders informed.

### Procedure

1. Pick the highest-priority **ready** work package from the plan (a package is ready
   when its dependencies are complete).
2. Implement in small units: code + tests in the same change; follow the layering rules
   in [architecture.md](technical/architecture.md).
3. Run locally: `pytest`, then manual smoke of the affected route.
4. Commit with a message naming the change (`add …`, `fix …`) — small, single-topic
   commits.
5. Update affected documents in the **same** change (requirements/architecture/API/…).
6. Record new issues in [issue-log.md](execution/issue-log.md); reassess [risk-management-plan.md](planning/risk-management-plan.md)
   if the work introduces new risks.
7. Mark the package done only when acceptance criteria in
   [requirements.md](planning/requirements.md) are met.

### Deliverables (built)

| Work package | Outcome | Date |
| --- | --- | --- |
| Data + repository | `data/quran.json` loaded through `QuranRepository` | 2026-08-23 |
| Search engine | Normalizer, inverted index, ranking, highlighting | 2026-08-23 → 08-27 |
| Test suite | 71 tests across 6 modules | 2026-08-23 |
| Reading UI | Surah list, surah reader, verse context, RTL layout | 2026-08-27 → 09-05 |
| Passage search | Fuzzy route + template | 2026-09-05 |
| Containerization | Dockerfile, requirements pinning, docker-compose | 2026-09-05 → 09-07 |
| Reverse proxy + TLS | Nginx config, Certbot volumes | 2026-10-06 |
| SEO & analytics | sitemap, robots.txt, GA4, Umami | 2026-10-01 → 10-07 |
| Documentation hub | `docs/` repository (Step 1) | 2026-10-08 |

### Entry / exit criteria

- **Entry:** plan baselined.
- **Exit:** all in-scope work packages delivered and passing acceptance criteria.

### This project's record

Execution: **2026-08-23 → 2026-10-07** (core build in August–September; deployment and
integration in October).

---

## Phase 4 — Monitoring & Controlling

**Documents (`docs/execution/`):** [status-report.md](execution/status-report.md), [meeting-minutes.md](execution/meeting-minutes.md), [progress-updates.md](execution/progress-updates.md), [issue-log.md](execution/issue-log.md), [risk-management-plan.md](planning/risk-management-plan.md)


**Purpose:** Measure performance against the baseline plan and correct deviations.
Runs continuously alongside Execution.

### Procedure

1. **Progress tracking** — plan vs. actual per work package; `git log` plus
   [changelog.md](changelog.md) are the progress record.
2. **Quality control** — run the full test suite on every change (`pytest`). No change
   merges with a failing suite (see [testing.md](technical/testing.md)).
3. **Requirement verification** — walk the traceability table in
   [requirements.md](planning/requirements.md); confirm each `Implemented` requirement still
   behaves as specified.
4. **Defect control** — every failure goes to [issue-log.md](execution/issue-log.md) with
   severity, root cause and resolution; re-opened issues are escalated.
5. **Risk monitoring** — review [risk-management-plan.md](planning/risk-management-plan.md) at each release;
   watch for triggers (e.g. "certificate expiry date approaching").
6. **Change control** — no unmanaged scope creep:
   1. Request: describe the change and the requirement it affects.
   2. Impact: update scope, schedule, cost, risk (reference the affected `docs/` file).
   3. Approve: owner approves or rejects.
   4. Implement: update code **and** documentation together; log in
      [changelog.md](changelog.md).
   5. Verify: tests + smoke test.
7. **Corrective/preventive action** — if an issue repeats (e.g. analytics config broke
   twice), add a regression test or checklist item rather than fixing it again ad hoc.

### Deliverables

Issue log, updated risk register, changelog, test results, change requests, status
reports (release notes in [changelog.md](changelog.md)).

### Entry / exit criteria

- **Entry:** execution underway.
- **Exit:** acceptance criteria met, open issues closed or deferred by decision,
  variances resolved.

### This project's record

Visible in history: post-release fixes such as environment-variable loading
(2026-10-06), Google Tag Manager / Umami (2026-10-06 → 10-07), Nginx config fixes
(2026-10-07), and the test-literal corrections during suite construction (2026-08-23).
These are logged in [issue-log.md](execution/issue-log.md).

---

## Phase 5 — Closing

**Documents (`docs/closing/`):** [final-project-report.md](closing/final-project-report.md), [lessons-learned.md](closing/lessons-learned.md), [closing-documentation.md](closing/closing-documentation.md)


**Purpose:** Formally complete the project or release: hand over the deliverable,
obtain acceptance, capture lessons learned, archive knowledge.

### Procedure

1. Confirm all in-scope requirements are `Implemented` (or explicitly deferred in
   [requirements.md](planning/requirements.md) §4).
2. Run the release gate: full test suite + manual smoke checklist
   (see acceptance criteria in [requirements.md](planning/requirements.md) §5 and the
   post-deploy checklist in [deployment.md](technical/deployment.md)).
3. Deploy to production and verify HTTPS, headers, and the 404/error pages.
4. **Obtain stakeholder acceptance** — sign-off recorded as a release tag/commit
   referencing the changelog entry.
5. **Deliver** the finished product: production URL + README quick start for handover.
6. **Archive documentation** — `docs/` is the handover package; nothing lives only in
   someone's head or chat history.
7. **Lessons learned** — conduct a short review (what went well, what didn't, what to
   change) and write it to [lessons-learned.md](closing/lessons-learned.md).
8. Close or transfer open issues; carry unresolved risks into the next release's
   register.
9. Tag the release in Git.

### Deliverables

Accepted product, release notes (changelog), lessons-learned record, archived docs,
final issue/risk status.

### Entry / exit criteria

- **Entry:** monitoring shows acceptance criteria met.
- **Exit:** stakeholder acceptance recorded, lessons learned documented, release tagged.

### This project's record

The running system has been in operation since 2026-10-07. Closing activity for the
documentation initiative (Steps 1–2) is the current phase: hub repository, lifecycle
procedure and management artifacts committed to `docs/`.

---

## Procedure summary (checklist per release)

| # | Phase | Key action | Evidence |
| --- | --- | --- | --- |
| 1 | Initiation | Approve charter | Committed charter |
| 2 | Planning | Baseline requirements, plan, risks | `docs/` baseline commit |
| 3 | Execution | Build work packages, tests + docs per change | Commits, changelog |
| 4 | Monitoring | Test suite green, issues/risks tracked, changes approved | issue log, risk plan |
| 5 | Closing | Smoke + deploy, accept, lessons learned, tag | release tag, lessons-learned |

## Document roles in the lifecycle

| Document | Initiation | Planning | Execution | Monitoring | Closing |
| --- | --- | --- | --- | --- | --- |
| Project charter (in this file) | ● | | | | |
| [project-plan.md](planning/project-plan.md) | | ● | ◐ | ◐ | |
| [requirements.md](planning/requirements.md) | | ● | ◐ | ● | ● |
| [issue-log.md](execution/issue-log.md) | | | ● | ● | ◐ |
| [risk-management-plan.md](planning/risk-management-plan.md) | | ● | | ● | ● |
| [lessons-learned.md](closing/lessons-learned.md) | | | | | ● |
| [changelog.md](changelog.md) | | | ● | ● | ● |

● primary · ◐ secondary
