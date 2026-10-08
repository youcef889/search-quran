# Project Charter

**Phase:** Initiation · **Status:** Approved (baseline: 2026-08-23)
Approval record: the committing of this charter to Git constitutes formal authorization
to proceed. Changes require owner sign-off via change control
([project-plan.md](../planning/project-plan.md) §9).

| Field | Content |
| --- | --- |
| **Project name** | Quran App — bilingual Qur'an reader & search engine |
| **Sponsor / owner** | Project owner (sole approver) |
| **Problem statement** | Existing Qur'an readers offer weak search that breaks on Qur'anic orthography — tashkeel, dagger alif and alef/hamza variants make naive matching unreliable |
| **Project objective** | Deliver a web application that browses all 114 surahs and searches the full text robustly, preserving full diacritics in display and highlighting |
| **Measurable goals** | 114 surahs browsable · multi-word search returns correctly ranked results · full test suite green · site live over HTTPS |
| **High-level scope** | See [scope-statement.md](scope-statement.md) |
| **Key deliverables** | Reader UI, keyword search, passage search, test suite, Dockerized HTTPS deployment, documentation repository |
| **Stakeholders** | See [stakeholder-analysis.md](stakeholder-analysis.md) |
| **Budget / resources** | 1 developer (part-time), open-source stack, existing host + domain — no paid services |
| **High-level schedule** | M1 core engine (Aug) → M3 UI (Sep) → M5 production (Oct) → M6 documentation (Oct) — detail in [project-plan.md](../planning/project-plan.md) §4 |
| **Top risks** | Certificate expiry, orthography misses, bus factor — see [risk-management-plan.md](../planning/risk-management-plan.md) |
| **Success criteria (acceptance)** | Release gate in [requirements.md](../planning/requirements.md) §5 |
| **Authority** | Owner approves scope changes; development team executes; all decisions recorded as ADRs |
| **Out of scope** | Accounts, database, mobile apps, admin CMS, second reading (Warsh) |

## Problem → objective → success

```
Problem: unreliable search on Qur'anic orthography
   └── Objective: robust search + faithful reading experience
         └── Success: verified by test suite, acceptance criteria, live HTTPS site
```

## Related initiation documents

- [scope-statement.md](scope-statement.md) — what is in, what is out, constraints, assumptions
- [stakeholder-analysis.md](stakeholder-analysis.md) — who is involved, their interest and influence
