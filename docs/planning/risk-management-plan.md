# Risk Management Plan & Register

Identified risks, assessed and reviewed at every release. Probability/Impact scale:
1 (low) – 5 (high); **Score = P × I**. Response: `Avoid` · `Reduce` · `Transfer` · `Accept`.

**Last review:** 2026-10-08 · **Next review:** before next release (WP13).

| ID | Risk | P | I | Score | Response | Mitigation / trigger | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-001 | TLS certificate expiry breaks HTTPS | 2 | 5 | 10 | Reduce | Certbot renewal scheduled (`certbot renew` twice daily + Nginx reload); trigger: expiry < 30 days → alert | Dev/Ops | Open, monitored |
| RISK-002 | Server compromise via exposed secret (`SECRET_KEY` default) | 2 | 5 | 10 | Reduce | `SECRET_KEY` must come from `.env` (git-ignored); production checklist verifies it is not the `dev-secret-change-me` default | Dev | Open |
| RISK-003 | Data file corruption → empty/broken app at startup | 2 | 4 | 8 | Reduce | `data/quran.json` versioned in Git (restore path); startup fails fast on bad JSON; add integrity check (114 surahs) to release gate | Dev | Open |
| RISK-004 | Malicious/very long query degrades performance | 2 | 3 | 6 | Reduce | Hard caps: `MAX_QUERY_LENGTH=200`, `MAX_PER_PAGE=100`, `MAX_PAGE`, passage `limit` ≤ 100; index read-only, no request-time I/O | Dev | Closed (mitigated by design) |
| RISK-005 | Search results wrong for some orthography (missed dagger-alif variants) | 3 | 4 | 12 | Reduce | Both dagger variants indexed (ADR-002); normalizer + highlighting tests; passage search as tolerant fallback | Dev | Open, monitored |
| RISK-006 | Scope creep (accounts, CMS, second reading) delays release | 3 | 3 | 9 | Avoid | Explicit out-of-scope list in [scope-statement.md](../initiation/scope-statement.md) §2 and [requirements.md](requirements.md) §4; all additions via change control | Owner | Open |
| RISK-007 | Single-developer bus factor — knowledge loss | 4 | 4 | 16 | Reduce | Central `docs/` repository as single source of truth; ADRs; test suite as executable spec | Dev | Reduced (Step 1) |
| RISK-008 | Silent analytics/SEO regressions after deploys (recurring issue class) | 3 | 2 | 6 | Reduce | CSP/security-header assertions + smoke checklist; see ISSUE-003/-004 preventive action | Dev | Open |
| RISK-009 | Host/resource exhaustion from traffic spikes (no DB, but 4 gunicorn workers) | 2 | 3 | 6 | Accept | Static responses, cheap rendering; revisit worker count and caching if p95 latency rises | Dev/Ops | Accepted |
| RISK-010 | Nginx config error causes downtime (hit in ISSUE-006) | 3 | 4 | 12 | Reduce | `nginx -t` before reload; config committed in Git for instant rollback | Dev | Reduced |
| RISK-011 | Wrong or unverified Arabic expectations reintroduced into tests | 3 | 3 | 9 | Reduce | Derive expected strings from the dataset, never type them from memory (L3); CI runs full suite | Dev | Open |
| RISK-012 | `.env` accidentally committed | 2 | 5 | 10 | Avoid | `.env` in `.gitignore`; never logged; rotate if exposed | Dev | Open, monitored |

## Escalation triggers

Escalate to the project owner immediately when: any risk scores ≥ 15, a new S1 issue
appears, or a mitigation trigger fires (e.g. certificate < 30 days).

## Review procedure

1. At each release: walk this register top-down.
2. Re-score open risks; close mitigated ones with a note.
3. Add risks surfaced by new work packages or new entries in
   [issue-log.md](../execution/issue-log.md).
4. Record the review date above.
