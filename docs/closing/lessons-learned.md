# Lessons Learned

Retrospective knowledge captured at each closing. Newest entries first.
Format: **Lesson → Context → Action / rule now in force.**
Source reviews: initial build (2026-08-23), hardening (2026-10-07), documentation
initiative (2026-10-08).

---

## Review: 2026-10-08 — documentation initiative (Steps 1–2)

**L1 — Documentation must live in Git, and ignore rules must allow it.**
Context: `.gitignore` contained `*.md`, so no new markdown document could ever be
version-controlled; docs were bound to be lost.
Action: `!docs/**/*.md` re-included; `docs/` is the single source of truth with an
index. Never add rules that make the knowledge base unversionable.

**L2 — Duplicated facts drift; link instead of copy.**
Context: README, routes and behavior descriptions overlapped and were already stale
(e.g. it referenced `services/quran.py`, which no longer exists).
Action: README holds overview + quick start only; every detail has one home in `docs/`
and is referenced by link.

---

## Review: 2026-10-07 — hardening & production rollout

**L3 — Never write expected Arabic text from memory in tests.**
Context: the initial suite failed repeatedly because expected literals were misspelled
or misremembered, producing false failures (ISSUE-002).
Action: derive expectations from `data/quran.json` or fixture values; treat unexplained
test failures as suspected test bugs first, verify against the dataset.

**L4 — Config/observability changes need their own smoke check.**
Context: GA4, GTM and Umami each needed a follow-up fix after "done" (ISSUE-003, -004);
three commits for what should have been one.
Action: after any config or CSP change: `curl -I` the site, verify headers, script
loading and the analytics hit before closing the task.

**L5 — Validate infrastructure config before reload, not after.**
Context: Nginx needed a post-deploy fix round (ISSUE-006).
Action: `nginx -t` (and `docker compose config`) are mandatory pre-deploy steps; the
checklist lives in [deployment.md](../technical/deployment.md).

**L6 — Small, single-topic commits made the timeline auditable.**
Context: `git log` alone reconstructs the phase history used in
[project-lifecycle.md](../project-lifecycle.md).
Action: keep commits scoped to one change; write messages that name the change.

---

## Review: 2026-08-23 — initial build

**L7 — Index once at startup; keep requests stateless.**
Context: naive per-request loading would repeat file I/O and index work.
Action: repository and search service are built in `create_app()` and shared read-only
via `app.extensions`; no request mutates shared state (safe across workers).

**L8 — Model the domain's ambiguity explicitly.**
Context: dagger alif (U+0670) can be read as alif or dropped; one convention made some
queries fail silently.
Action: index both normalized variants (ADR-002); prefer explicit dual handling over
guessing a single "correct" reading.

**L9 — Separate precise search from tolerant search.**
Context: AND semantics are right for browse queries but return nothing for a pasted
quotation with one typo.
Action: two endpoints — `/search` strict, `/search/passage` fuzzy with threshold
(ADR-003); never weaken one to compensate for the other.

**L10 — A tiny, realistic fixture beats mocking.**
Context: needed deterministic tests that still exercise real Qur'anic orthography.
Action: `TINY_QURAN` in `conftest.py` (real tashkeel/dagger alif, 2 surahs); unit tests
use it, integration tests use the real dataset.

**L11 — Clamp input at the boundary; never trust the client.**
Context: page/per_page/threshold/limit could drive expensive or nonsensical requests.
Action: all limits are hard caps in `config.py`, applied in route helpers — clients can
only be clamped, never exceeded.

---

## Recurring themes → standing rules

| Theme | Standing rule |
| --- | --- |
| Config/observability slips | Smoke checklist after every config change (L4) |
| Expectations typed from memory | Derive test expectations from data (L3) |
| Knowledge scattered or unversionable | Everything in `docs/`, links not copies (L1, L2) |
| Infrastructure validated late | `nginx -t` / `docker compose config` before deploy (L5) |

## How to add a lesson

1. At closing, answer: *What went well? What didn't? What do we change?*
2. Add an entry under the review date with Context and Action.
3. If the lesson creates a permanent rule, add it to the relevant checklist
   ([project-plan.md](../planning/project-plan.md) §6, [deployment.md](../technical/deployment.md),
   [testing.md](../technical/testing.md)) — a lesson with no attached rule will be forgotten.
