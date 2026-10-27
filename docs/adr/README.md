# Architecture Decision Records

One file per significant decision, MADR style ([template](0000-template.md)). Change a decision by writing a new ADR that supersedes the old one, and log it in the [reconciliation register](../requirements/06-reconciliation-register.md).

| ADR | Decision | Status |
|---|---|---|
| [0001](0001-django-modular-monolith.md) | Django modular monolith | Proposed |
| [0002](0002-server-rendered-htmx-alpine-tailwind.md) | Server-rendered UI with HTMX, Alpine.js and Tailwind (no SPA) | Proposed |
| [0003](0003-server-side-sessions-instead-of-jwt.md) | Server-side sessions instead of JWT | Proposed |
| [0004](0004-postgresql-postgis-search-for-mvp.md) | PostgreSQL + PostGIS + pg_trgm search for the MVP | Proposed |
| [0005](0005-postgres-row-locking-credit-ledger.md) | PostgreSQL row-locking credit ledger (no Kafka) | Proposed; supported by 0013 |
| [0006](0006-celery-redis-transactional-outbox.md) | Celery + Valkey background jobs with a transactional outbox | Proposed; outbox built in M0 |
| [0007](0007-payment-gateway-adapter.md) | Payment gateway adapter (Stripe + PayPal) | Proposed |
| [0008](0008-aws-ecs-fargate-terraform.md) | AWS ECS Fargate + Terraform | **Superseded by 0014** |
| [0009](0009-s3-direct-upload-async-image-processing.md) | Direct-to-S3 upload with asynchronous image processing | Proposed; amended by 0014 (any S3-compatible storage) |
| [0010](0010-field-level-pii-encryption-blind-indexes.md) | Field-level PII encryption with blind indexes | Proposed; OQ-29 open; key custody amended by 0014 |
| [0011](0011-feature-flags-django-waffle.md) | Feature flags with django-waffle | Accepted (M0) |
| [0012](0012-local-s3-emulator-seaweedfs.md) | SeaweedFS as the local S3 emulator | Accepted (M0) |
| [0013](0013-debit-concurrency-spike-results.md) | Credit-debit concurrency spike results | Accepted locally; RDS run pending |
| [0014](0014-portable-hosting-paas-and-self-hosted.md) | Portable hosting on PaaS or a self-hosted VPS | **Accepted** (client decision) |
