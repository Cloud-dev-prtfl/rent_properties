# CLAUDE.md

Rent Property Listing: a credit-based rental marketplace (listers post properties; renters spend credits to reveal a lister's contact). Built as a **Django 5.2 LTS modular monolith** with server-rendered templates, HTMX, Alpine.js and Tailwind, on PostgreSQL 17 + PostGIS, Valkey/Redis and Celery, packaged as one container image that deploys to a PaaS (Render, Railway, Heroku, Fly.io) or self-hosted servers (Docker Compose, Kamal, Coolify), per ADR-0014. AWS is **not** the target.

## Current state

**M0 (foundations) is done locally**: repo, tooling, settings, `apps.core` (outbox, audit, health, logging), the custom `accounts.User`, Celery, the UI shell, docker compose, tests (98 % coverage) and CI checks. **Hosting (ADR-0014, 2026-10-27):** portable PaaS or self-hosted; manifests exist (`render.yaml`, `fly.toml`, `heroku.yml`, `Procfile`, `deploy/compose`, `deploy/kamal`); actual deployment is deferred. The GitHub repo will be provided by the user. Next milestone: M1 (identity and accounts). The design knowledge base is in `docs/` (start at `docs/README.md`). Client inputs (SRS .docx files and AI-generated diagrams) are in `ProjectDocuments/`, which is local only (git-ignored, confidential; the GitHub repo is public). They contain known errors, so read `docs/requirements/03-gap-analysis-and-decisions.md` before trusting them.

## How we build

- **Chunked, milestone by milestone** (M0 → M7), never big-bang. The current milestone's scope, stories and exit criteria are in `docs/delivery/02-milestones-and-backlog.md`. Do not build ahead of the active milestone.
- Each story must meet `docs/delivery/05-definition-of-done-and-workflow.md`.
- Requirements are not frozen. If something in the docs is wrong or unachievable, propose the change; don't silently diverge. Record it as an ADR in `docs/adr/` and an entry in `docs/requirements/06-reconciliation-register.md`.

## Source of truth when docs disagree

1. Accepted ADRs in `docs/adr/`
2. `docs/requirements/06-reconciliation-register.md`
3. The owning doc for the topic (listed in the register §1): schema → `design/01-domain-model.md`; credit algorithms → `design/02-credit-wallet-and-ledger.md`; URLs, settings names, layout → `architecture/03-codebase-structure.md`

## Non-negotiables (money path)

- Credits are integers; money is integer minor units + ISO-4217 currency.
- Every balance change goes through `apps.credits.services` (`grant_credits` / `debit_credits`) in one DB transaction: wallet row locked `SELECT … FOR NO KEY UPDATE`, append-only hash-chained `CreditLedgerEntry`, `CHECK (balance >= 0)`, and unique idempotency keys.
- Show Number costs 2 credits (`CREDITS_REVEAL_COST`) and the signup promo is 10 (`CREDITS_SIGNUP_PROMO`). A repeat reveal of the same property is free.
- Side effects (emails, etc.) go through the transactional outbox / `on_commit`; never send from inside the transaction.
- A lister's contact details never reach the HTML, htmx partials or caches before a paid reveal.
- Payments: credits are fulfilled only after gateway-verified confirmation (webhook or a server-side API check), idempotently, via `payments.services.fulfill_order`. Raw card data never touches our servers.

## Code conventions (details in `docs/architecture/03-codebase-structure.md`, `docs/delivery/03-engineering-standards.md`)

- Layout: `config/` (settings: base/local/test/production), `apps/<app>/` with thin models and views. Writes go in `services.py` (verb-first names) and reads in `selectors.py`. Templates are in `templates/` plus `<app>/partials/_*.html`.
- Apps: core, accounts, listings, search, geo, credits, leads, payments, notifications, analytics, moderation (verification is post-MVP).
- Tooling: uv, ruff (lint and format), mypy + django-stubs, pytest-django + factory_boy, Playwright, axe-core. Tests run on PostgreSQL + PostGIS, never SQLite. Coverage gate is 90% on `apps/`.
- Run Python tooling **in the dev container** (GDAL lives there): `make check`, `make test`, or `docker compose run --rm --no-deps -e DJANGO_SETTINGS_MODULE=config.settings.test web <cmd>`. The stack: `make up`.
- When adding an app, add it to `LOCAL_APPS` and to the import-linter `layers` contract in `pyproject.toml`.
- **Portability rules (ADR-0014):** config only through env vars; no cloud SDK calls outside adapters; object storage only via the S3-compatible API (django-storages); email via SMTP/Anymail; metrics via OpenTelemetry; no writes to the container filesystem; new process types go in `bin/` + every manifest; schedules go in Celery beat, not platform cron. Older docs that mention AWS services are read through the ADR-0014 mapping table.
- Conventional Commits; trunk-based development with short-lived branches; every PR is reviewed.
