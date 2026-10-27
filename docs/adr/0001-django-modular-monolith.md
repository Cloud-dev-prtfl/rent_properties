# ADR-0001: Django modular monolith

Decides the overall architecture style: one Django project, deployed as one container image, organised into layered Django apps whose boundaries are enforced in CI.

Status: Draft v0.1 (2026-10-21)

| | |
|---|---|
| Decision status | Proposed |
| Date | 2026-10-21 |
| Deciders | Tech Lead (owner); PO acknowledges |
| Consulted | Platform, Security, QA |
| Supersedes / superseded by | — |
| Requirements | SRS §1 (scalable marketplace, high transaction volume), §5.2–5.3 (atomic check + debit), §8.2 (1,000 debits/s), §10.1 (cloud native, horizontal scale), §10.2 (SOLID, peer review, ≥ 90 % coverage); NFR-SCAL-01, NFR-CODE-01 |
| Gap / open question | Known issue #18 (Ops Console in MVP); A-4 (traffic forecast) |
| Related | [01 §2, §6, §10, §16](../architecture/01-system-architecture.md) · [03 Codebase structure](../architecture/03-codebase-structure.md) · [02 Tech stack T2–T3](../architecture/02-tech-stack.md#2-technology-choices-by-layer) |

## Context and problem statement

The client's architecture diagram already shows a "Django Monolith" with views, ORM models (User, PropertyListing, Lead, CreditWallet, Transaction), templates and an Ops Console. The SRS demands an **atomic** credit check and debit with an immutable ledger (§5.2–5.3), 1,000 credit transactions per second (§8.2), horizontal scalability across global markets (§10.1), and SOLID code with at least 90 % coverage (§10.2). Requirements are not frozen, so the structure must absorb change cheaply. The team is small (reference team of a few engineers, or a solo developer with an AI pair; [delivery §9](../delivery/01-development-approach.md#9-team-assumptions-and-timeline)).

The core use case, "Show Number", touches four concerns in one step: the wallet and ledger (`credits`), the reveal record (`leads`), the listing (`listings`) and the receipt email trigger (`core` outbox). They must commit together or not at all.

**Question:** how should the system be decomposed and deployed so that the money path is strongly consistent, delivery is fast, and the codebase stays maintainable as it grows?

## Decision drivers

1. **Transactional integrity on the money path.** Debit, reveal record and outbox message in one ACID transaction (SRS §5.2–5.3, known issue #10).
2. **Delivery speed** for an incremental M0–M7 plan with a small team.
3. **Operational simplicity**: few moving parts to deploy, monitor and secure.
4. **Maintainability**: clear boundaries, testability, SOLID (SRS §10.2) and protection against a "big ball of mud" (risk AR-3).
5. **Horizontal scalability** of the stateless tier (SRS §10.1).
6. **Built-in back-office capability** for the Ops Console (moderation, tag-change review, fraud review; known issue #18).
7. **Evolvability**: ability to extract a component later if evidence demands it.

## Considered options

1. **Modular monolith on Django**: layered Django apps, HackSoft-style service layer, boundaries enforced by import-linter.
2. **Conventional Django monolith** with no enforced boundaries (apps import each other's models freely).
3. **Microservices** (identity, listings, search, credits, payments, notifications as separately deployed services).
4. **Serverless functions** (API Gateway + Lambda + managed queues).
5. **Monolith on another Python framework** (FastAPI + SQLAlchemy + a separate admin).

## Decision outcome

**Chosen option 1: a Django 5.2 LTS modular monolith on Python 3.13**, because it is the only option that gives a single ACID transaction for the money path, the fastest delivery for a small team, and the Django admin as the base of the Ops Console, while keeping internal boundaries strict enough to extract modules later.

Decision details (normative; full text in [01 §6 and §10](../architecture/01-system-architecture.md#10-modular-monolith-boundary-rules)):

| Topic | Rule |
|---|---|
| Apps and layers | `core` (L0); `accounts`, `geo`, `analytics` (L1); `listings`, `credits` (L2); `leads`, `payments`, `search`, `verification` (L3); `moderation`, `notifications` (L4). An app may import only from lower layers; same-layer apps are independent |
| Public API of an app | `services` (writes), `selectors` (reads), `exceptions`, `enums`/`constants`, `types` (DTOs), `signals`. Everything else is private |
| Data ownership | One owning app per table; no cross-app writes; cross-app foreign keys only point downward, as string references |
| Transactions | Services own `transaction.atomic()`; `ATOMIC_REQUESTS=False`; no network I/O inside a transaction; side effects after commit via the outbox ([ADR-0006](0006-celery-redis-transactional-outbox.md)) |
| Coupling across layers | Lower layers publish documented signals or outbox topics; higher layers subscribe. No `post_save` business logic |
| Third-party SDKs | Only inside adapter sub-packages (`payments/gateways/`, `geo/providers/`, `accounts/integrations/`, `notifications/channels/`, `core/storage.py`, `core/crypto/`) |
| Deployment | One image; process types `web`, `worker`, `worker-media`, `beat`, `migrate` ([04 §6](../architecture/04-infrastructure-and-deployment.md#6-compute-ecs-services-and-the-container-image)) |
| Ops Console | **In MVP**: hardened Django admin plus custom staff views under `/ops/` in the `moderation` app |

### Consequences

- **Positive:**
  - Show Number is one short PostgreSQL transaction across `credits`, `leads` and `core`. There are no distributed transactions, sagas or compensations on the money path.
  - One repository, one pipeline, one image: lower operational load, simpler security review, one place for tests (coverage gate is meaningful).
  - Django admin, auth, forms, i18n and GeoDjango cover large parts of the SRS without custom infrastructure.
  - The stateless web tier scales horizontally; the data tier scales vertically plus read replicas, which covers the SRS targets ([NFR §4](../quality/02-nfr-performance-and-scalability.md#4-capacity-model-and-sizing-assumptions)).
- **Negative:**
  - All modules release together: a defect in one area blocks a release of all. *Mitigation:* small PRs, trunk-based development, feature flags, automatic rollback ([04 §8.4](../architecture/04-infrastructure-and-deployment.md#84-deployment-strategy)).
  - A single primary database is the scaling ceiling for writes. *Mitigation:* short transactions, per-wallet locks, replicas for reads, a measured scaling ladder ([ADR-0005](0005-postgres-row-locking-credit-ledger.md)); extraction seams for later.
  - Boundaries erode without discipline. *Mitigation:* import-linter contracts and Semgrep rules are CI-blocking from M0; architecture review on PRs touching more than one app.
  - The test suite grows with the whole system. *Mitigation:* `pytest -n auto`, per-app test selection locally, 10-minute PR budget ([testing §16](../delivery/04-testing-strategy.md#16-ci-pipeline-and-matrix)).
- **Neutral / follow-on:** future extraction candidates (search, payments, notifications, media processing, public API) and their triggers are listed in [01 §16](../architecture/01-system-architecture.md#16-future-extraction-seams).

### Confirmation

- import-linter `layers` and `forbidden` contracts, plus the custom public-API contract, pass on every PR from M0.
- Semgrep rule `foreign-model-write` has no findings.
- M4 exit: the Show Number debit, reveal and outbox commit atomically under the concurrency tests ([testing §7](../delivery/04-testing-strategy.md#7-concurrency-tests-for-credit-debit)) and the 1,000 debits/s load test (PT-03).
- Quarterly architecture review of the app dependency graph (generated from import-linter) against [01 §6](../architecture/01-system-architecture.md#6-c4-level-3-components-of-the-monolith-django-apps).

## Pros and cons of the options

### 1. Modular monolith on Django (chosen)

- Good, because one database transaction covers the money path.
- Good, because the admin, auth, forms, templates, i18n and GeoDjango are mature and integrated.
- Good, because boundaries are explicit and machine-checked, so later extraction is a contained change.
- Bad, because enforcing boundaries needs tooling and review effort from day one.
- Bad, because one deployable unit couples release cadence across modules.

### 2. Conventional Django monolith (no enforced boundaries)

- Good, because it is the fastest to start.
- Bad, because cross-app model access spreads quickly; the credit ledger could be written from anywhere, which undermines the SRS integrity requirements (§9.2).
- Bad, because extraction later becomes a rewrite.

### 3. Microservices

- Good, because services scale and deploy independently.
- Bad, because Show Number would span services (credits, leads, notifications): it needs a saga or two-phase commit, which conflicts with "atomic" (SRS §5.2) and "display immediately" (SRS §5.4).
- Bad, because of the operational cost: service discovery, many pipelines, distributed tracing as a necessity, network failure modes, per-service databases. That cost is not justified by a small team or by the expected load (1,000 debits/s is reachable on one PostgreSQL primary; [ADR-0005](0005-postgres-row-locking-credit-ledger.md)).
- Bad, because the domain boundaries are not yet stable (requirements are not frozen); wrong service boundaries are expensive to move.

### 4. Serverless functions

- Good, because there is no server management and costs scale to zero.
- Bad, because server-rendered HTML with sessions, Celery-style background work and long-lived database connections fit poorly (connection storms need a proxy; cold starts affect the latency targets).
- Bad, because a Django-sized feature set would be split into many functions, recreating the microservice problems.

### 5. Monolith on FastAPI + SQLAlchemy

- Good, because of async I/O and typed APIs.
- Bad, because admin, auth flows (email verification, reset, MFA, sessions), forms and templating would have to be assembled or built; the SRS needs all of them.
- Bad, because a JSON-first framework pushes towards an SPA, which [ADR-0002](0002-server-rendered-htmx-alpine-tailwind.md) rejects for the MVP.

## Deviations from the SRS

None. The SRS does not prescribe an architecture style; the client diagram already shows a Django monolith. The service layer and enforced boundaries are additions that the diagram does not show ([01 §7](../architecture/01-system-architecture.md#7-mapping-the-clients-architecture-diagram-to-this-design)).

## Follow-ups

| # | Action | Owner | Milestone |
|---|---|---|---|
| 1 | Add import-linter contracts and the custom public-API contract to CI | Tech Lead | M0 (US-002) |
| 2 | Semgrep rule `foreign-model-write` | Tech Lead | M0 |
| 3 | Re-evaluate extraction seams against real metrics | Tech Lead | Post-launch review |

## More information

- Revisit when any trigger in [01 §16](../architecture/01-system-architecture.md#16-future-extraction-seams) fires, when a second team needs independent release cadence, or when a native mobile API is scheduled (it calls the same services; no extraction required).
