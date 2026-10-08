# Architecture Decision Records

Lightweight ADRs: one file section per decision. Format — **Context / Decision /
Consequences**. Newest last. Never delete an ADR; supersede it with a new one that
links back.

---

## ADR-001 — In-memory search index instead of a database or search service

- **Status:** Accepted
- **Date:** 2025-09-05

**Context.** The dataset is ~6k verses, fully read-only, shipped in the image. A
database or Elasticsearch would add operational surface for no benefit.

**Decision.** Load `data/quran.json` once at process start; build the search index and
inverted index in memory; expose them read-only through `app.extensions`.

**Consequences.** Zero external dependencies and no request-time file I/O; changing data
requires a restart; memory is duplicated per Gunicorn worker (acceptable at this size).

---

## ADR-002 — Index both dagger-alif interpretations

- **Status:** Accepted
- **Date:** 2025-09-05

**Context.** Dagger alif (U+0670) in Qur'anic orthography can be read as an alif or
omitted. A single convention would make some queries silently fail.

**Decision.** Store two normalized variants per verse (`dagger_as_alef=True/False`) and
index tokens from both into the same inverted index.

**Consequences.** Retrieval is correct under either reading; index entries roughly
double; ranking checks both variants when scoring phrase matches.

---

## ADR-003 — AND semantics for keyword search, fuzzy search as a separate route

- **Status:** Accepted
- **Date:** 2025-09-19

**Context.** Users paste quotations that may contain typos or missing diacritics, but
multi-word browse queries should stay precise.

**Decision.** `/search` uses strict AND retrieval over the inverted index.
`/search/passage` uses `rapidfuzz.partial_ratio` with a configurable threshold for
tolerant matching.

**Consequences.** Precise results stay precise; typos get an explicit, discoverable
fallback; two code paths to maintain and test.

---

## ADR-004 — Application factory + layered modules

- **Status:** Accepted
- **Date:** 2025-10-01

**Context.** Tests needed an isolated app instance; routes had started coupling to data
loading.

**Decision.** `create_app(config)` factory in `app.py`; blueprints in `routes/`;
domain logic in `services/`; JSON access in `repositories/`. Dependencies flow
routes → services → repositories.

**Consequences.** Tests build apps with `TestConfig`; the data source can be swapped;
shared state lives in `app.extensions`, built once per process.

---

## ADR-005 — Nginx + Certbot + Docker Compose as the production topology

- **Status:** Accepted
- **Date:** 2025-10-06

**Context.** The app must be served over HTTPS on a single host with automatic
certificate renewal.

**Decision.** Two-container compose stack: the app (Gunicorn, internal port 4000) behind
`nginx:alpine` terminating TLS, with Certbot volumes for issuance/renewal and
bind-mounted logs.

**Consequences.** Single-command deploys; app port is never published to the host;
certificate renewal needs a scheduled `certbot renew` plus an Nginx reload.

---

## ADR-006 — Documentation centralized in `docs/`

- **Status:** Accepted
- **Date:** 2026-10-08

**Context.** Requirements, operational notes and behavior specs were either missing or
scattered; `.gitignore` ignored `*.md`, so documents could not be version-controlled.

**Decision.** All project documentation lives in `docs/` with an index
(`docs/README.md`), `*.md` stays ignored at the root but `!docs/**/*.md` is
re-included, and every behavior change must update the affected document in the same
PR.

**Consequences.** One source of truth with Git-backed history; discipline required to
keep docs in lockstep with code; ad-hoc markdown notes outside `docs/` remain ignored.
