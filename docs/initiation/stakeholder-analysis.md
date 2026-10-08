# Stakeholder Analysis

**Phase:** Initiation · **Baseline:** 2026-10-08 · **Review:** each release closing

Stakeholders are identified, classified by power/interest, and mapped to a
communication approach. The execution detail (channels, frequency) lives in the
[communication plan](../planning/communication-plan.md).

## 1. Register

| ID | Stakeholder | Role | Interest | Influence | Power/Interest grid | Engagement |
| --- | --- | --- | --- | --- | --- | --- |
| STK-1 | Project owner | Sponsor, approver, host of domain/infra | High | High | **Manage closely** — keep satisfied and informed at every gate | Approves charter, scope changes, releases |
| STK-2 | Developer(s) | Builder of all deliverables; maintainer | High | High | **Manage closely** — day-to-day decisions via docs | Executes WBS, updates `docs/` |
| STK-3 | End users (Arabic readers) | Primary audience for reading & search | High | Medium | **Keep satisfied** — quality of text and search decides adoption | Feedback via search correctness, speed, RTL rendering |
| STK-4 | End users (English readers / researchers) | Search + translation-facing usage | Medium | Medium | **Keep satisfied** | Bilingual UI, search ranking quality |
| STK-5 | Search engines (Google, crawlers) | Discoverability of the site | Medium | Medium | **Keep informed** — automated, via `sitemap.xml` / `robots.txt` | SEO artifacts |
| STK-6 | Analytics providers (Umami, GA4) | Measurement tools, privacy constraints | Low | Low | **Monitor** — external services shape CSP | Script tags, CSP allowances |
| STK-7 | Let's Encrypt / Certbot | TLS certificate authority/agent | Medium | High (availability) | **Monitor** — failure blocks HTTPS | Automated renewal, expiry monitoring |
| STK-8 | Hosting/ops (VPS provider) | Runtime environment | Medium | High (uptime) | **Keep satisfied** | Resource limits, restart policies |
| STK-9 | Future contributors | Extend the project | Medium | Medium | **Keep informed** — `docs/` is the onboarding path | README + docs index |

## 2. Expectations & how they are met

| Stakeholder | Key expectation | Response in the project |
| --- | --- | --- |
| Owner | Working site, no unpaid surprises, controllable scope | Change control, risk register, no-cost stack |
| Users | Correct, fast, diacritically faithful results | Test suite, dual dagger-alif indexing, caps on request cost |
| Crawlers | Stable URLs, indexable pages | `sitemap.xml`, `robots.txt`, server-rendered HTML |
| Providers | Correct configuration | Deployment checklist, `nginx -t`, CSP documentation |

## 3. Influence/interest summary

- **Manage closely:** owner, developer.
- **Keep satisfied:** end users, hosting.
- **Keep informed:** crawlers, future contributors.
- **Monitor:** analytics providers, Certbot.

## 4. Risks tied to stakeholders

| Risk | Linked |
| --- | --- |
| Bus factor — knowledge concentrated in one developer | RISK-007 → mitigated by the documentation repository |
| User trust lost through wrong text/search results | RISK-005 → dual normalization + tests |
| HTTPS outage perceived as project failure | RISK-001 → certificate monitoring |

## 5. Review procedure

At each closing: re-check the register for new/removed stakeholders, update engagement
approaches, and feed changes into the [communication plan](../planning/communication-plan.md).
