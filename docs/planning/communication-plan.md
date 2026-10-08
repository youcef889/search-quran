# Communication Plan

**Phase:** Planning · **Baseline:** 2026-10-08 · **Owner:** project owner
Derived from the stakeholder register ([stakeholder-analysis.md](../initiation/stakeholder-analysis.md)).

## 1. Communication matrix

| # | What | Channel / artifact | Frequency | Audience | Author | Response time |
| --- | --- | --- | --- | --- | --- | --- |
| C1 | Progress updates | Git commits (single-topic messages) | Every change | Owner, developers | Developer | — |
| C2 | Status report | [status-report.md](../execution/status-report.md) | Weekly / end of phase | Owner | Developer | Owner review ≤ 3 days |
| C3 | Phase progress narrative | [progress-updates.md](../execution/progress-updates.md) | Per phase | All stakeholders | Developer | — |
| C4 | Meeting minutes | [meeting-minutes.md](../execution/meeting-minutes.md) | Per meeting (kickoff, gate review, retrospective) | All | Note-taker | Circulated same day |
| C5 | Issue reporting | [issue-log.md](../execution/issue-log.md) | As discovered | Owner, developers | Anyone | S1 same day, S2 ≤ 3 days |
| C6 | Risk alerts | [risk-management-plan.md](risk-management-plan.md) escalation triggers | On trigger | Owner | Developer | Immediate |
| C7 | Change requests | Change-control record in [project-plan.md](project-plan.md) §9 | Per request | Owner (approver) | Requester | Decision ≤ 2 days |
| C8 | Release notes | [changelog.md](../changelog.md) | Per release | All | Developer | At release |
| C9 | Decisions | [decisions.md](../technical/decisions.md) (ADRs) | Per decision | All | Developer | At decision |
| C10 | Handover / final report | [final-project-report.md](../closing/final-project-report.md) | Closing | Owner, future maintainers | Developer | At closing |
| C11 | Operational alerts | App logs (stdout) + `nginx-logs/` | Continuous | Developer/ops | System | Triaged on next review |

## 2. Channels of record (single source of truth)

| Purpose | Canonical location |
| --- | --- |
| Anything technical | `docs/technical/` |
| Anything phase-related | `docs/<phase>/` |
| Chronology | `git log`, [changelog.md](../changelog.md) |
| Secrets | `.env` — **never** discussed in writing, never committed |

Chat, email and verbal agreements are **not** records: decisions must land in an
`docs/` artifact to be valid.

## 3. Escalation path

```
Developer (detects issue/risk)
   └── logs issue / scores risk
         └── S1 or score ≥ 15 ──► Project owner (immediate)
         └── otherwise ──► next status report
```

## 4. Meeting cadence

| Meeting | When | Agenda | Output |
| --- | --- | --- | --- |
| Kickoff | Initiation | Charter review | Approved charter |
| Release gate review | Before each release | Requirements traceability, open issues/risks, release gate | Go / no-go decision in minutes |
| Retrospective | After each release | What went well / didn't / change | Entry in [lessons-learned.md](../closing/lessons-learned.md) |
| Ad hoc | On S1 issue or major change request | Incident or change | Minutes + decision |

## 5. Rules

1. Status reports are snapshots; the changelog is the chronology — don't duplicate both.
2. Any decision without an artifact in `docs/` did not happen.
3. Reports never contain secrets or full environment values.
