# Rent Property Listing — Engineering Knowledge Base

Design and delivery documentation for the Rent Property Listing web application: a credit-based rental marketplace built as a **Django modular monolith**. It is derived from the client's SRS v1.0 (2025-10-25) and architecture diagram, kept in a local `ProjectDocuments/` folder that is **not published** (confidential client material; git-ignored).

Status: Draft v0.1 (2026-10-22, updated 2026-10-27). M0 is built; hosting is portable (PaaS or self-hosted, [ADR-0014](adr/0014-portable-hosting-paas-and-self-hosted.md)). The client's requirements are **not frozen**: every deviation from the SRS is recorded with its reason.

## Start here

| If you want to… | Read |
|---|---|
| Understand what we are building and why it differs from the SRS | [Requirements catalog](requirements/02-requirements-catalog.md) → [Gap analysis and decisions](requirements/03-gap-analysis-and-decisions.md) |
| Know what is still undecided | [Open questions](requirements/04-open-questions.md) (OQ-01 monetisation model, OQ-29 login email, OQ-33 launch markets, OQ-49 Product Owner) |
| Resolve a conflict between two documents | [Reconciliation register](requirements/06-reconciliation-register.md); it wins over every other doc |
| See the architecture in one page | [System architecture](architecture/01-system-architecture.md) |
| Start building | [Development approach](delivery/01-development-approach.md) → [Milestones and backlog](delivery/02-milestones-and-backlog.md) |

## Document map

### Requirements (`requirements/`)

| Doc | Purpose |
|---|---|
| [01 Source documents](requirements/01-source-documents.md) | Inventory of client inputs, diagram transcriptions, and how far each can be trusted |
| [02 Requirements catalog](requirements/02-requirements-catalog.md) | Every SRS requirement as an atomic, testable item with an ID, MoSCoW priority, acceptance criteria and milestone |
| [03 Gap analysis and decisions](requirements/03-gap-analysis-and-decisions.md) | Contradictions, errors and infeasible items in the SRS and diagram, with the adjustment we made |
| [04 Open questions](requirements/04-open-questions.md) | Stakeholder questions, the milestone each one blocks, and the default we proceed with |
| [05 Glossary](requirements/05-glossary.md) | Domain terms (credit, ledger, reveal, lister tag, price book, …) |
| [06 Reconciliation register](requirements/06-reconciliation-register.md) | Cross-document rulings and precedence rules |

### Architecture (`architecture/`, `adr/`)

| Doc | Purpose |
|---|---|
| [01 System architecture](architecture/01-system-architecture.md) | C4 views, app boundaries, sync/async paths, caching, scaling, mapping to the client diagram |
| [02 Tech stack](architecture/02-tech-stack.md) | Every technology choice with reasons and alternatives |
| [03 Codebase structure](architecture/03-codebase-structure.md) | Repo tree, per-app layout, settings, URL map, layering rules (services/selectors) |
| [05 Hosting and deployment](architecture/05-hosting-and-deployment.md) | **Current.** Portable deployment to PaaS (Render, Railway, Heroku, Fly.io) or self-hosted (Compose, Kamal, Coolify): processes, env vars, scaling, backups, hardening |
| [04 Infrastructure and deployment](architecture/04-infrastructure-and-deployment.md) | *Superseded AWS design (ECS, RDS, Terraform)*, kept for reference |
| [ADR-0001 … 0014](adr/) | Architecture decision records ([index](adr/README.md)): modular monolith, HTMX UI, sessions vs JWT, Postgres search, row-locking ledger, Celery outbox, payment adapter, S3 direct upload, PII encryption, feature flags, local S3 emulator, concurrency spike results, **portable hosting (0014)** |

### Design (`design/`)

| Doc | Purpose |
|---|---|
| [01 Domain model](design/01-domain-model.md) | Schema of record: all models, constraints, indexes, state machines, ERD |
| [02 Credit wallet and ledger](design/02-credit-wallet-and-ledger.md) | Append-only hash-chained ledger, atomic debit/grant algorithms, audit, 1,000 TPS plan |
| [03 Contact reveal flow](design/03-contact-reveal-flow.md) | "Show Number": UX state matrix, sequence, idempotency, email, abuse controls |
| [04 Identity and access](design/04-identity-and-access.md) | Custom user, allauth, verification/OTP, sessions, promo grant, RBAC matrix |
| [05 Listings and media](design/05-listings-and-media.md) | Multi-step listing wizard, drafts, lister tag rules, image pipeline, My Properties |
| [06 Search and discovery](design/06-search-and-discovery.md) | PostGIS + pg_trgm + full-text search, filters, caching, SEO, saved properties |
| [07 Payments and credit purchase](design/07-payments-and-credit-purchase.md) | Packages, price books, Stripe/PayPal flows, webhooks, 5-second allocation, reconciliation |
| [08 Notifications](design/08-notifications.md) | Email/SMS catalogue, outbox dispatch, deliverability, preferences |
| [09 External integrations](design/09-external-integrations.md) | Every third-party provider: adapter, config, failure handling, data shared |

### Quality and operations (`quality/`)

| Doc | Purpose |
|---|---|
| [01 Security and compliance](quality/01-security-and-compliance.md) | Threat model, OWASP/ASVS controls, encryption, PCI DSS SAQ-A scope |
| [02 NFR: performance and scalability](quality/02-nfr-performance-and-scalability.md) | Latency/throughput targets, capacity model, load-test plan |
| [03 Observability and operations](quality/03-observability-and-operations.md) | Logging, metrics, alerts, SLOs, backups and restore testing, releases |
| [04 Runbooks](quality/04-runbooks.md) | Incident runbooks (payment outage, ledger mismatch, DB degradation, …) |
| [05 Privacy and data protection](quality/05-privacy-and-data-protection.md) | PII inventory, GDPR / India DPDP, retention, erasure vs immutable ledger |

### Delivery and UX (`delivery/`, `ux/`)

| Doc | Purpose |
|---|---|
| [01 Development approach](delivery/01-development-approach.md) | Why chunked vertical slices, milestone dependency graph, risk register |
| [02 Milestones and backlog](delivery/02-milestones-and-backlog.md) | M0–M7 + Post-MVP: epics, user stories, exit criteria, demo scripts |
| [03 Engineering standards](delivery/03-engineering-standards.md) | Code style, migrations, Git workflow, reviews, documentation |
| [04 Testing strategy](delivery/04-testing-strategy.md) | Test pyramid, concurrency tests, E2E journeys, coverage gates |
| [05 Definition of Done and workflow](delivery/05-definition-of-done-and-workflow.md) | DoR/DoD, PR and release checklists |
| [UX and page inventory](ux/01-ux-and-page-inventory.md) | Sitemap, every page, header/dropdown, Show Number states, design tokens, accessibility |

## Milestones at a glance

| | Milestone | Outcome |
|---|---|---|
| M0 | Foundations & walking skeleton | Repo, tooling, CI, docker compose, base layout, portable deployment manifests (**done locally**) |
| M1 | Identity & accounts | Sign-up, verification, login/logout, reset, profile, header dropdown, RBAC |
| M2 | Listings | Multi-step form + drafts, image pipeline, geocoding, tags, My Properties |
| M3 | Search & discovery | Filters, fuzzy + geo search, sorting, caching, saved properties |
| M4 | Credits & contact reveal | Wallet, ledger, promo grant, Show Number debit, receipt email, history |
| M5 | Payments | Packages, localized prices, Stripe + PayPal, webhooks, reconciliation |
| M6 | Ops console & moderation | Moderation queue, tag-change review, fraud flags, ledger audit dashboard |
| M7 | Hardening & launch | Choose and provision hosting (ADR-0014), 1,000 TPS load test, pen test, a11y audit, restore drill, go-live |

## Conventions

- Requirement IDs: `FR-AUTH-xx`, `FR-LIST-xx`, `FR-CRED-xx`, `FR-PAY-xx`, `FR-PROF-xx`, `NFR-…`. Stories: `US-xxx`. Gaps: `GAP-xx`. Open questions: `OQ-xx`.
- "**Deviation from SRS:**" marks a deliberate change and "**Assumption:**" an unconfirmed premise.
- Changing a decision: write or supersede an ADR, update the owning document, and log the change in the reconciliation register.
