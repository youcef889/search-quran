# Documentation Hub — Quran App

This directory is the **single source of truth** for the project: requirements,
management artifacts, technical specifications and operational runbooks — all
versioned in Git alongside the code.

Documents are organized **by lifecycle phase, with cross-phase subject matter kept
separately** (Step 3 of the documentation process):

```
docs/
├── README.md              ← this index
├── project-lifecycle.md   ← phases & procedure (how the folders are used)
├── changelog.md           ← chronology of all changes
├── initiation/            ← Phase 1: charter, scope, stakeholders
├── planning/              ← Phase 2: plan, requirements, risks, communication
├── execution/             ← Phases 3–4: status, progress, minutes, issues
├── closing/               ← Phase 5: final report, lessons, handover checklist
└── technical/             ← subject matter: how the product works & is operated
```

## Index by phase

### 1. Initiation — `initiation/`
| Document | Purpose |
| --- | --- |
| [project-charter.md](initiation/project-charter.md) | Formal authorization: problem, objective, goals, stakeholders, success criteria |
| [scope-statement.md](initiation/scope-statement.md) | Product scope, boundaries, deliverables, constraints, assumptions |
| [stakeholder-analysis.md](initiation/stakeholder-analysis.md) | Stakeholder register, power/interest grid, engagement strategy |

### 2. Planning — `planning/`
| Document | Purpose |
| --- | --- |
| [project-plan.md](planning/project-plan.md) | Baseline plan: scope, WBS, schedule, budget, quality, change control |
| [requirements.md](planning/requirements.md) | Functional & non-functional requirements, acceptance criteria, traceability |
| [risk-management-plan.md](planning/risk-management-plan.md) | Risk identification, scoring (P×I), mitigations, escalation triggers |
| [communication-plan.md](planning/communication-plan.md) | Channels, cadence, escalation path, meeting schedule |

### 3–4. Execution & Monitoring/Control — `execution/`
| Document | Purpose |
| --- | --- |
| [status-report.md](execution/status-report.md) | Periodic status snapshots: scope/schedule/quality/risk/resources |
| [progress-updates.md](execution/progress-updates.md) | Phase-by-phase progress narrative against the WBS |
| [meeting-minutes.md](execution/meeting-minutes.md) | Kickoff, gate reviews, retrospectives — decisions and actions |
| [issue-log.md](execution/issue-log.md) | Problem log: defects, root causes, resolutions, recurring analysis |

### 5. Closing — `closing/`
| Document | Purpose |
| --- | --- |
| [final-project-report.md](closing/final-project-report.md) | Objectives vs. results, deliverable status, acceptance & sign-off |
| [lessons-learned.md](closing/lessons-learned.md) | Retrospectives converted into standing rules |
| [closing-documentation.md](closing/closing-documentation.md) | Closing checklist and handover package |

### Subject matter (all phases) — `technical/`
| Document | Purpose |
| --- | --- |
| [architecture.md](technical/architecture.md) | System overview, components, data flow, project layout |
| [api.md](technical/api.md) | HTTP endpoints, parameters, limits, response shapes |
| [search-engine.md](technical/search-engine.md) | Normalization, inverted index, ranking, highlighting, passage search |
| [configuration.md](technical/configuration.md) | Config classes, environment variables, tunable limits |
| [deployment.md](technical/deployment.md) | Docker, Gunicorn, Nginx, Certbot, production runbook |
| [testing.md](technical/testing.md) | Test suite layout, fixtures, how to run |
| [data.md](technical/data.md) | Datasets, schemas, provenance |
| [decisions.md](technical/decisions.md) | Architecture Decision Records (ADRs) |

### Cross-cutting — root
| Document | Purpose |
| --- | --- |
| [project-lifecycle.md](project-lifecycle.md) | Phases & procedure: how every artifact is produced and used |
| [changelog.md](changelog.md) | Reverse-chronological change log |

The root [README.md](../README.md) stays short: overview and quick start only.

## Where does a new document go?

| The document is about… | Put it in… |
| --- | --- |
| Why/whether the project exists (charter, scope, stakeholders) | `initiation/` |
| How the work will be done (plans, requirements, risks, comms) | `planning/` |
| How work is going (status, progress, minutes, issues) | `execution/` |
| Wrap-up (final report, lessons, handover) | `closing/` |
| The product itself (design, API, ops, tests, data, ADRs) | `technical/` |

## Rules for this repository

1. **One home per topic.** If a fact is written here, do not duplicate it elsewhere.
   Link instead.
2. **Phase folders are mandatory.** Every lifecycle phase keeps its artifacts in its
   folder — see [project-lifecycle.md](project-lifecycle.md).
3. **Docs travel with code.** Any change in behavior updates the affected document in
   the same change.
4. **Git is the version control.** `docs/**/*.md` is explicitly un-ignored in
   `.gitignore`. Never add docs to ignore rules.
5. **No secrets.** Environment variables are documented by *name and purpose* only;
   values live in `.env` (ignored) or the deployment secret store.
6. **Dates are ISO-8601** (`YYYY-MM-DD`) in reports, changelogs and ADRs.

## Contributing a new document

1. Choose the folder with the table above.
2. Create the file using the structure of an existing document in that folder.
3. Add a row to the matching index table above.
4. Link it from any related document and from the phase in
   [project-lifecycle.md](project-lifecycle.md) if it is phase-specific.
5. Record the addition in [changelog.md](changelog.md).
