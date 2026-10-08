# Changelog

Project and documentation change log. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); dates are ISO-8601.
Reverse chronological.

## [Unreleased]

### Added
- Documentation organized by lifecycle phase and subject (Step 3): folders
  `initiation/`, `planning/`, `execution/`, `closing/`, `technical/` — 2026-10-08.
- New phase artifacts: `initiation/project-charter.md`, `initiation/scope-statement.md`,
  `initiation/stakeholder-analysis.md`, `planning/communication-plan.md`,
  `execution/status-report.md`, `execution/progress-updates.md`,
  `execution/meeting-minutes.md`, `closing/final-project-report.md`,
  `closing/closing-documentation.md` — 2026-10-08.
- Project lifecycle documentation (Step 2): phases & procedure
  (`project-lifecycle.md`), baseline project plan (`project-plan.md`), issue log
  (`issue-log.md`), risk register (`risk-management-plan.md`), lessons learned
  (`lessons-learned.md`) — 2026-10-08.
- Central documentation repository under `docs/` (index, requirements, architecture,
  API, search engine, configuration, deployment, testing, data, ADRs) — 2026-10-08.
- `.gitignore` now re-includes `docs/**/*.md` so documentation is version-controlled —
  2026-10-08.

### Changed
- Technical documents moved from `docs/` root to `docs/technical/`; management
  artifacts moved to their phase folders; `risk-register.md` renamed to
  `planning/risk-management-plan.md`; all cross-links updated — 2026-10-08.

## [2026-10-07]

### Added
- Umami analytics script in `templates/base.html`.

### Fixed
- Environment variable loading; application security/headers tweaks.

## [2026-10-06]

### Added
- Nginx service in `docker-compose.yml`; Certbot volumes; nginx config and logs.
- Google Analytics 4 (`GA_MEASUREMENT_ID`).

### Fixed
- Nginx configuration files.

## [2026-10-03]

### Added
- `sitemap.xml` and `robots.txt`.

## [2025-10-01]

### Added
- Layered refactor: `repositories/`, `services/` split
  (`normalizer.py`, `quran_search.py`, `surah_names.py`), blueprint split
  (`routes/main.py`, `routes/search.py`).
- Passage (fuzzy) search and JSON search endpoints.
- Test suite: normalization, keyword search, highlighting, pagination, passage, routes.

---

When adding an entry: group by `Added` / `Changed` / `Fixed` / `Removed`, keep it
one line per change, and reference the affected `docs/` document if behavior is
specified there.
