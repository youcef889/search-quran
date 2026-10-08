# Meeting Minutes

**Phase:** Monitoring & Control · **Cadence:** per meeting (C4 in the
[communication plan](../planning/communication-plan.md))
Minutes are circulated the same day and kept here as the permanent record. Newest first.

---

## MIN-004 — Documentation review (Steps 1–3)

- **Date:** 2026-10-08 · **Attendees:** owner, developer
- **Type:** Gate review · **Agenda:** approve the central documentation repository and
  its phase/subject organization

**Discussion**
- Step 1 (centralization): single source of truth in `docs/`, Git-versioned; `*.md`
  ignore rule had made versioning impossible — corrected.
- Step 2 (lifecycle): phases mapped to the project's real timeline; charter, plan,
  issue log, risk register and lessons learned established.
- Step 3 (organization): documents arranged by phase (`initiation/`, `planning/`,
  `execution/`, `closing/`) with subject matter under `technical/`.

**Decisions**
- D-014: `docs/` is the only documentation home; links instead of copies.
- D-015: artifacts are mandatory per phase — charter + scope + stakeholders (initiation),
  plan + requirements + risk + communication (planning), status + minutes + progress
  (execution), lessons + final report + closing checklist (closing).

**Actions**

| # | Action | Owner | Due |
| --- | --- | --- | --- |
| A-011 | Audit all internal links after restructuring | Dev | 2026-10-08 ✅ |
| A-012 | Record structure change in changelog | Dev | 2026-10-08 ✅ |

---

## MIN-003 — Retrospective (production hardening)

- **Date:** 2026-10-07 · **Attendees:** owner, developer · **Type:** Retrospective

**What went well:** production stack delivered (Docker, Nginx, TLS, analytics); small
single-topic commits made the history auditable.
**What didn't:** three follow-up commits for analytics/env configuration (ISSUE-003,
ISSUE-004); Nginx config needed a fix round (ISSUE-006).

**Decisions**
- D-011: config/CSP changes require a smoke check (`curl -I`, script load, analytics hit)
  before closing the task.
- D-012: `nginx -t` / `docker compose config` mandatory before any reload.

**Actions:** both rules written into [lessons-learned.md](../closing/lessons-learned.md)
(L4, L5) and [deployment.md](../technical/deployment.md). ✅

---

## MIN-002 — Release gate review (M4 containerization)

- **Date:** 2026-09-07 · **Attendees:** owner, developer · **Type:** Gate review

**Discussion:** reading UI and passage search complete; compose file added; README
published.
**Decision:** D-009 — release accepted for staging; production work (proxy/TLS) moves
to M5.
**Actions:** schedule Nginx + Certbot configuration (→ WP10). ✅

---

## MIN-001 — Kickoff

- **Date:** 2026-08-23 · **Attendees:** owner, developer · **Type:** Kickoff / initiation

**Discussion:** problem (search unreliable on Qur'anic orthography), objective (robust
search + faithful reading), constraints (no database, single developer, open-source
stack), success criteria (114 surahs, ranked AND search, green suite, HTTPS live).
**Decisions:** D-001 in-memory index at startup; D-002 dual dagger-alif normalization;
D-003 strict AND search with fuzzy passage fallback.
**Actions:** baseline charter and requirements; begin WP1 (data layer).

---

## Template

```
## MIN-nnn — Title
Date · Attendees · Type (Kickoff / Gate review / Retrospective / Ad hoc) · Agenda
Discussion → Decisions (D-nnn) → Actions (A-nnn: owner, due date)
```
