# ADR-0011: Feature flags with django-waffle

Decides how features are switched on and off without a deploy: kill switches for incidents, gradual rollout of new flows, and per-market enablement.

Status: Draft v0.1 (2026-10-27)

| | |
|---|---|
| Decision status | Accepted (M0) |
| Date | 2026-10-27 |
| Deciders | Tech Lead |
| Consulted | Platform, QA |
| Supersedes / superseded by | — |
| Requirements | NFR-AVAIL-01 (incident mitigation), NFR-MAINT-01 |
| Gap / open question | US-014 seed ADR |
| Related | [Observability §14.3 kill switches](../quality/03-observability-and-operations.md), [Runbooks](../quality/04-runbooks.md), register R-52 |

## Context and problem statement

The runbooks rely on operational kill switches (for example `ratelimit_db_fallback`, `phone_otp_enabled`, `turnstile_login_always`), and later milestones need gradual rollout (PayPal per market, SSO). Config changes through environment variables need a redeploy, which is too slow for an incident.

## Decision drivers

- Flip in seconds, without a deploy, audited.
- Works in a server-rendered monolith (templates, views, Celery tasks).
- Stored in our own PostgreSQL: no new vendor, no extra network dependency on the request path.

## Considered options

1. **django-waffle** (flags, switches, samples; DB-backed with caching).
2. Environment variables / settings only.
3. Hosted flag service (LaunchDarkly, Unleash, Flagsmith).

## Decision outcome

**Option 1, django-waffle 5.x.** Switches serve as kill switches, flags handle user and percentage rollouts, and samples are for sampling. Names are `snake_case` (codebase §11). `WAFFLE_CREATE_MISSING_*` is off: every flag is created by a data migration, so a typo cannot silently create a new, disabled flag.

### Consequences

- **Positive:** no deploy to mitigate incidents; flags are visible in the ops admin; zero vendor cost.
- **Negative:** flag reads touch the cache/DB. waffle caches them, and a cache outage falls back to the DB (acceptable per RB-05).
- **Neutral / follow-on:** every flag needs an owner and a removal date. Stale flags are reviewed at each milestone exit.

### Confirmation

`waffle` is installed with its middleware (M0). The first switches arrive with the runbook-backed features (M1 OTP, M4 reveal fallbacks).

## Pros and cons of the options

- **Settings only:** simplest, but needs a deploy (minutes) and cannot target users or percentages.
- **Hosted service:** richest targeting and analytics, but adds cost, a third-party dependency on the request path, and personal-data sharing.

## Deviations from the SRS

None.

## Follow-ups

- Data migration creating the operational switches listed in observability §14.3 (M1/M4).
- Ops-console view of switch changes in the audit log (M6).
