# Reconciliation Register

The single, authoritative list of cross-document inconsistencies in `docs/` and how each is settled. The design documents were written in parallel by specialist authors, and each recorded its own "consistency notes". This register consolidates them and gives one ruling per item.

Status: Draft v0.1 (2026-10-22)

## 1. Precedence rules

1. **This register wins.** Where a document disagrees with a ruling here, follow the ruling. The document is corrected when its area is next touched; that correction PR closes the item here.
2. Otherwise each topic has an **owning document**, which wins over documents that only mention the topic:

| Topic | Owning document |
|---|---|
| Requirement wording, IDs, acceptance criteria | [02-requirements-catalog](02-requirements-catalog.md) |
| Deviations from the SRS and their rationale | [03-gap-analysis-and-decisions](03-gap-analysis-and-decisions.md) |
| Schema (models, fields, constraints, indexes) | [design/01-domain-model](../design/01-domain-model.md) |
| Credit algorithms, ledger, hash chain | [design/02-credit-wallet-and-ledger](../design/02-credit-wallet-and-ledger.md) |
| URL map, settings names, repo layout, templates, queues | [architecture/03-codebase-structure](../architecture/03-codebase-structure.md) |
| AWS, environments, secrets inventory, CI/CD | [architecture/04-infrastructure-and-deployment](../architecture/04-infrastructure-and-deployment.md) |
| Alert thresholds, SLOs, kill switches | [quality/03-observability-and-operations](../quality/03-observability-and-operations.md) |
| Copy, page behaviour, accessibility patterns | [ux/01-ux-and-page-inventory](../ux/01-ux-and-page-inventory.md) |
| Story scope and milestone placement | [delivery/02-milestones-and-backlog](../delivery/02-milestones-and-backlog.md) |

3. An accepted ADR (`docs/adr/`) overrides all of the above for its decision.

## 2. Already applied (2026-10-22)

| ID | Change | Files |
|---|---|---|
| A-01 | Setting names: `REVEAL_COST_CREDITS` → `CREDITS_REVEAL_COST`; `SIGNUP_PROMO_CREDITS` → `CREDITS_SIGNUP_PROMO` (app-prefix convention) | requirements/02, 03, 05 |
| A-02 | `PAYMENTS_GATEWAYS_BY_REGION` → `PAYMENTS_GATEWAYS_BY_MARKET` (the registry is keyed by market) | architecture/03, 04 |
| A-03 | `fulfil_order` → `fulfill_order` (canonical service and OTel span name) | design/02, requirements/02, 03, 05, delivery/02 |
| A-04 | Image aspect ratio in the M2 decision table: 4:3–16:9 with auto-crop (was mis-cited as 3:4–2:1) | delivery/01 |
| A-05 | Pending-order reconciliation every **5 min** (was 10 min) | architecture/01 §9 |
| A-06 | Debit lock shown as `SELECT … FOR NO KEY UPDATE` | architecture/01 §8 |

The consistency tables inside individual documents (for example UX §17.2, ADR-0007 and ADR-0010 "Consistency items") still describe these items in their original form. They are historical notes; this table is current.

### 2.1 Decided while building M0 (2026-10-27)

| ID | Decision | Where |
|---|---|---|
| A-07 | **Email uniqueness:** emails are stored lower-cased, enforced by `CHECK (email = lower(email))`, with a plain unique index `uq_user_email`. This gives case-insensitive uniqueness with one index that exact login lookups use, so it supersedes the `lower(email)` functional index in domain model §3.1 and resolves R-22 for `accounts_user`. allauth's `EmailAddress` table is still checked in M1. | `apps/accounts/models.py` |
| A-08 | **Local PostGIS image:** `imresamu/postgis:17-3.5` (multi-arch build by a postgis/docker-postgis maintainer); the official `postgis/postgis` image is amd64-only. Local only; production uses RDS. | `compose.yaml` |
| A-09 | **Python tooling runs in the dev container** (GDAL/GEOS are not needed on developer machines); `make check` wraps it. CSS builds on the host with the pinned, SHA-verified Tailwind CLI. | `Makefile` |
| A-10 | **Static publishing:** only `static/dist`, `static/vendor` and `static/src/js` are published (prefixes `dist/`, `vendor/`, `js/`); Tailwind sources are never collected. | `config/settings/base.py` |
| A-11 | **Spike result:** both debit variants are correct under contention and exceed 1,000 debits/s locally ([ADR-0013](../adr/0013-debit-concurrency-spike-results.md)); the RDS run is pending. | `tests/load/spike_debit.py` |

### 2.2 Hosting decision: portable PaaS or self-hosted (2026-10-27)

The client replaced AWS with portable hosting ([ADR-0014](../adr/0014-portable-hosting-paas-and-self-hosted.md); guide: [architecture/05](../architecture/05-hosting-and-deployment.md)). These rulings **override every AWS-specific statement** in other documents, including rulings R-46, R-48, R-52, R-55, R-57 and R-59 below.

| ID | Ruling | Status |
|---|---|---|
| H-01 | Deployment target is portable: PaaS (Render, Railway, Heroku, Fly.io) or self-hosted (Docker Compose, Kamal, Coolify). ADR-0008 and architecture/04 are superseded and kept for reference only. | Decided |
| H-02 | Processes are `bin/web`, `bin/worker`, `bin/beat` (exactly one), `bin/release`. The three Celery queues are unchanged; a dedicated media worker is just another `bin/worker` with `CELERY_QUEUES=media` (replaces "two ECS services" in R-46). | Implemented |
| H-03 | Cache aliases (R-48) are unchanged in code. On a single Redis/Valkey instance, cache, sessions, rate-limit and broker share it with `maxmemory-policy noeviction` and TTLs on every cache key; separate instances are optional. `REDIS_URL` is accepted. | Implemented |
| H-04 | Migrations run through `manage.py release` under a PostgreSQL advisory lock, on every target (replaces the ECS one-off migrate task). | Implemented |
| H-05 | `/healthz` and `/readyz` are answered before host validation and the HTTPS redirect (platform checkers use internal hosts over HTTP). | Implemented |
| H-06 | Client IP from `TRUSTED_PROXY_COUNT` or `CLIENT_IP_HEADER` (`apps.core.clientip`); audit and rate limits use it. | Implemented |
| H-07 | Gunicorn binds `$PORT`; the release ID falls back to platform variables; `DATABASE_SSLMODE` for managed DBs across networks. | Implemented |
| H-08 | Runbooks (quality/04) and alerts (quality/03) keep their procedures, but AWS CLI steps become platform commands (`render ssh`, `heroku run`, `fly ssh console`, `kamal app exec`, `docker compose exec`). Rewrite them for the chosen target before M7. The `ops-run` allow-list (R-52) becomes "management commands run through the platform's exec". | Open (needs OQ-50) |
| H-09 | Field-encryption keys come from secrets (`FIELD_ENCRYPTION_KEYS`, `FIELD_ENCRYPTION_ACTIVE_KEY`, `BLIND_INDEX_KEY`) instead of KMS; ADR-0010 is amended. Implement in M1. | Decided |
| H-10 | Media storage uses any S3-compatible provider (R2, B2, Hetzner, Spaces, S3); ADR-0009 is amended; SeaweedFS stays the local emulator. Implement in M2. | Decided |
| H-11 | Security controls without AWS: Cloudflare WAF/CDN in front (recommended on all targets), platform secret stores, LUKS full-disk encryption and off-host encrypted backups when self-hosted. | **Deferred** (client, 2026-10-27): self-hosted security hardening is decided with the production target |
| H-12 | Observability: stdout JSON + platform log drains or Loki; Sentry/GlitchTip; OTel OTLP to any backend; queue-depth and outbox-age as OTel metrics (replaces the CloudWatch publisher). | Decided |
| H-18 | PostGIS + pg_trgm remain **hard requirements** for every database (client confirmed 2026-10-27). | Decided |
| H-13 | PostgreSQL extensions: created by the first migrations (`postgis` by Django's backend, `pg_trgm` by `core.0002`). Where a provider forbids `CREATE EXTENSION`, enable them in its dashboard first. `infra/sql/bootstrap.sql` applies to self-hosted databases (replaces R-55's RDS role). | Decided |
| H-14 | No Nginx on any target (R-57): the platform router, Caddy, kamal-proxy or Traefik does TLS and routing, and WhiteNoise serves static files. The local dev compose keeps Nginx only as a convenience. | Implemented |
| H-15 | Deploy strategy per target (replaces R-59): see architecture/05 §2. The CI deploy job is written once the target is chosen. | Deferred |
| H-16 | 99.9 % availability needs ≥ 2 web instances and an HA or fast-restore database on every target; a single VPS is pilot/staging only. | **Client (2026-10-27):** the current hosting is treated as **staging**; production topology and HA are decided later |
| H-17 | SRS §10.1 (IaC with Terraform/CloudFormation) is met in intent through declarative manifests in the repo (`render.yaml`, `fly.toml`, `heroku.yml`, `Procfile`, `deploy/compose`, `deploy/kamal`). **Deviation from SRS** recorded in ADR-0014. | Decided |

## 3. Rulings: to be applied when the area is next edited

### 3.1 Credits, reveal and payments (M4–M5)

| ID | Item | Ruling | Source notes |
|---|---|---|---|
| R-01 | Debit locking mechanism | `SELECT … FOR NO KEY UPDATE` on the wallet row inside `atomic(durable=True)` with the retry wrapper at the outermost use case. The conditional `UPDATE` variant is not used, because the hash chain needs balance, `head_seq` and `head_hash` read under one lock. Codebase §12.2 and US-402 to align. | design/02 CN-1, design/03 CN-R2 |
| R-02 | Idempotency keys and outbox payloads | Public IDs only: `reveal:<user_public_id>:<property_public_id>`; payload `{"reveal": "<public uuid>"}`. No pre-transaction "already revealed" fast path; the lookup under the wallet lock covers duplicates. | design/02 CN-3, design/03 CN-R1 |
| R-03 | Wallet creation time | Created when the account becomes verified, in the same transaction as the promo grant. FR-CRED-07.1 intent ("automatic, no setup step") is unchanged. | gap CI-01, design/02 CN-2 |
| R-04 | Ledger field names | Domain model names are canonical: `server_process_id`, `request_id`, `app_release`, `entry_hash`, `reference_type` / `reference_id`. The catalog's `process_info` / `hash` are descriptive only. | gap CI-02, design/02 CN-4 |
| R-05 | Ledger partitioning (if ever needed) | Hash partitioning by `wallet_id`, not monthly range on `created_at` (unique constraints must include the partition key). Not required at MVP volume. | design/02 CN-6 |
| R-06 | Load-test seeding reason code | `LOADTEST` (not `perf_seed`). | design/02 CN-5 |
| R-07 | Promo for users verified before M4 | No batch backfill: trigger T2 grants the promo at the user's next login. US-401 / US-403 to drop the backfill. | identity CN-ID-4 |
| R-08 | Welcome email trigger | New outbox topic `credits.promo_granted`, published inside `grant_signup_promo`; NTF-09 subscribes to it, not to `account.verified`. | identity CN-ID-3 |
| R-09 | Reveal endpoint responses | Existing but unpublished listing → **200** with the `unavailable` block (htmx does not swap 404); unknown ID → 404. Add 429 and 500 to htmx `responseHandling` for the reveal component. The full listing detail page for an unavailable listing returns **410** (listings design §9.2); US-217 to align. | design/03 CN-R5, UX-C3 |
| R-10 | Header balance after a reveal or purchase | Out-of-band swap of the badge and dropdown balance in the same response (primary), plus refresh on tab focus. Periodic polling is **off by default** (`CREDITS_BADGE_POLL_SECONDS = 0`, configurable). Needs PO confirmation, because the catalog's NFR-UX-01.2 says 30 s polling. | gap CI-04, perf P-02, UX-C4, design/03 CN-R11 |
| R-11 | Show Number state machine | Adds `staff_account` (staff cannot transact) and the outcomes `charged_email_held`, `unavailable`, `own_listing`, `staff`, `challenge`, `busy`. "Own listing" has its own copy, not the insufficient-credit toast. | design/03 CN-R4, CN-R10 |
| R-12 | Reveal rate limits | 10/min, 30/h, 100/day per user (confirm under OQ-35). | design/03 CN-R9 |
| R-13 | Payment status polling | Server-driven: 1 s for the first 10 s, then 2 s up to 60 s. | UX-C6 |
| R-14 | Allocation latency target | **p99 ≤ 5 s** from gateway confirmation to visible balance (US-509 said p95). | gap CI-06 |
| R-15 | PCI scope wording | Stripe Checkout / PayPal hosted approval = SAQ A. An embedded iframe form may stay SAQ A-eligible only with the extra script controls in ADR-0007; anything else is SAQ A-EP. Tech-stack T15 to align. | ADR-0007 C2 |
| R-16 | Secret names | Infrastructure §10.2 path style `<provider>/<name>` is canonical. Twilio API key/secret replace the auth token at runtime; `stripe/secret-key` holds a **restricted** key. | integrations §13 #1, #3 |
| R-17 | Geocoding naming | `GeocodingProvider` = vendor port (adapters + contract tests); `geo.services` = the GeocodingService facade used by apps. | integrations §13 #10 |

### 3.2 Identity, accounts and privacy (M1)

| ID | Item | Ruling | Source notes |
|---|---|---|---|
| R-20 | allauth email verification mode | `ACCOUNT_EMAIL_VERIFICATION = "optional"`; transacting is gated by `can_transact` (verified email **or** phone). Recorded as a deviation from the baseline wording "mandatory". | identity CN-ID-1 |
| R-21 | Verification method | Email: HMAC links with POST confirmation, no codes. Remove the code field from UX A-02 unless OQ-NTF-02 decides otherwise. | identity CN-ID-2 |
| R-22 | Email lookup index | Add `upper(email)` functional indexes on `accounts_user` and `account_emailaddress` unless the pinned allauth already provides them (Django `iexact` uses `UPPER()`). | identity CN-ID-6 |
| R-23 | allauth usersessions writes | Verify at M1; throttle activity writes to one per 5 min per session if it writes per request. | identity CN-ID-7 |
| R-24 | Staff accounts | Staff cannot transact (no wallet, promo, reveals or listings). New model `accounts.StaffLinkedAccount` lists staff members' personal accounts for separation of duties. Superadmin holds `credits.approve_adjustment` for the cases in design/02 §10.1. | identity CN-ID-5, CN-ID-8 |
| R-25 | Admin URL | `ADMIN_URL_PREFIX = "ops/admin/"`, so the `/ops/` staff-MFA middleware covers it. | identity CN-ID-9 |
| R-26 | Signup form | Single password field with a "Show password" toggle (no confirmation field). | identity CN-ID-10 |
| R-27 | Field-level encryption format | `enc:v1:<key_version>:<base64(nonce ‖ ciphertext ‖ tag)>`; encrypted columns are `text` (not `bytea`); `core.FieldKey` gains `encryptions bigint NOT NULL DEFAULT 0` for the nonce budget. | ADR-0010 C1–C3 |
| R-28 | Front-end privacy settings | htmx `historyCacheSize: 0` (no revealed contacts in localStorage snapshots); `MESSAGE_STORAGE` = session storage (no toast text in cookies). | privacy writer |
| R-29 | Privacy journal retention | At least the longest backup retention + 30 days (not 90 days), if 12-month monthly snapshots are adopted. | runbooks / privacy |
| R-30 | New privacy models | `accounts.ConsentEvent`, `accounts.PrivacyRequest`, `accounts.IdentityBlock`; `SignupPromoClaim` retained ≤ 5 years; erasure also clears street address, postal code and exact location. Add to the domain model in M1. | privacy writer |

### 3.3 Platform, codebase and operations (M0)

| ID | Item | Ruling | Source notes |
|---|---|---|---|
| R-40 | URL map | Codebase §7 paths are canonical: `/my/properties/…`, `/my/properties/<uuid>/insights/`, `/my/saved/`, `/my/credits/`, `/my/credits/buy/`, `/payments/status/<uuid>/`, `/payments/receipt/<uuid>/`. Add `/pricing/`, `/help/…`, `/legal/…`, `/accessibility/`, `/accounts/signup/validate/`, `/my/verify/` (`accounts:verification-required`) and the `/ops/…` sub-paths when each route is built. Older aliases in the catalog and backlog (`/credits/buy/`, `/account/saved/`, `/account/transactions/`, `/my-properties/…`) are superseded. | UX-C1, UX-C2, gap CI-09, design/03 CN-R8 |
| R-41 | Template locations | Codebase §8.1: app partials in `<app>/partials/_*.html` (for example `listings/partials/_property_card.html`, `listings/property_detail.html`); generic components in `templates/components/`. | UX-C12 |
| R-42 | Design tokens | Tailwind v4 prefixed names (`--color-tag-agent-bg`, …) in `static/src/tokens.css`, imported by `app.css`. | UX-C9 |
| R-43 | Visible-only polling | `data-poll` attribute + an `htmx:beforeRequest` handler that cancels while `document.hidden`. No `hx-trigger` JS filters, because they need `eval`, which the CSP blocks. | codebase CS-3, UX-C5 |
| R-44 | CSP | Nonce-capable strict policy; no inline scripts in templates. | codebase CS-4 |
| R-45 | Service naming | Verb-first services (`publish_property`, `reveal_contact`), `core.outbox.publish`, `core.audit.record`, singular outbox topics. Listings design §12.1 and the backlog to align. | codebase CS-1, gap CI-08 |
| R-46 | Celery queues | Three queues, two worker services (codebase §10); a `critical` queue / `worker-critical` service is added only if load tests show fulfilment latency risk. | codebase CS-2, infra INF-D5 |
| R-47 | `verification` app | Not created until KYC is scheduled; the private bucket and storage alias are created in M2. | codebase CS-5 |
| R-48 | Cache aliases | `sessions` alias is fail-soft (`IGNORE_EXCEPTIONS=True`, falling back to the DB via `cached_db`). Rate-limit counters move to a dedicated **fail-closed** alias (`ratelimit`), so reveal, checkout and OTP limits refuse instead of silently allowing. | runbooks C-01, C-02 |
| R-49 | Enqueue during broker outage | `transaction.on_commit(fn, robust=True)` plus a short publish retry; the outbox sweeper (every 30 s) is the backstop. | runbooks C-03 |
| R-50 | Media durability | Sanitised masters are kept (`masters/*`, versioned, replicated); variants are regenerable from them. Observability §10.1 to align. | runbooks C-05 |
| R-51 | Alert thresholds | Observability §7 is the single catalogue; the payments (§19) and notifications (§15) tables link to it instead of restating numbers. | runbooks C-09 |
| R-52 | Ops tooling | Add `turnstile_login_always` kill switch, a staging-only `PAYMENTS_FAULT_INJECTION` setting, and the commands `ledger_diff`, `cache_flush`, `reprocess_stuck_images`, `notifications_unsuppress`, `dbdiag`, `credits_repair_wallet_head` (maker-checker) to the `ops-run` allow-list. | runbooks C-04, C-06–C-08, C-10 |
| R-53 | Missing runbook | Add **RB-15 "Non-payment provider degradation"** (maps/geocoding, Turnstile, Pwned Passwords, malware scanning, quota exhaustion) to quality/04 before M7. | integrations §13 #9 |
| R-54 | `idle_in_transaction_session_timeout` | 10 s (in `bootstrap.sql`); NFR §6.2's 30 s is superseded. | infra INF-C1 |
| R-55 | PostgreSQL extensions on RDS | Created by `bootstrap.sql` (PostGIS needs `rds_superuser`); the first `core` migration keeps `CREATE EXTENSION IF NOT EXISTS` for local and test. | infra INF-C3 |
| R-56 | Repo tree additions | Add `infra/ecs/`, `docker/gunicorn.conf.py`, `docker/postgres/init.sh`, `ops-task.yml`, `core/integrations/…` and the other adapter modules listed in integrations §13 #4 to codebase §2 / §5. | infra INF-C2, integrations §13 #4–5 |
| R-57 | Diagram's NGINX box | No Nginx in AWS: CloudFront + ALB + WhiteNoise + S3 (OAC) cover its roles. Nginx is used only in local docker compose. | infra INF-D1 |
| R-58 | Local S3 emulator | SeaweedFS (the MinIO community edition moved to source-only distribution); LocalStack S3 is the fallback. | infra INF-D2 |
| R-59 | Deploy strategy | ECS rolling deploys with circuit breaker + alarm rollback; ECS blue/green evaluated for prod `web` in M7. AWS adds a `shared` tooling account (ECR, apex DNS zone). | infra INF-D3, INF-D6 |

### 3.4 UX and test details

| ID | Item | Ruling | Source notes |
|---|---|---|---|
| R-70 | Promo label in transaction history | "Welcome credits". The M4 demo script and E2E J-01 to align. | UX-C7 |
| R-71 | Save toggle accessibility | Constant accessible name "Save {title}" + `aria-pressed`; visible "Saved" text only on the detail-page button. | UX-C10 |
| R-72 | Show Number E2E locator | `get_by_role("button", name=re.compile(r"Show Number\W+2 credits"))`; the middle dot is `aria-hidden`. | UX-C11 |
| R-73 | Saving a property | Requires a verified account (default); OQ-42 / OQ-SRCH-07 may relax it to login-only. | gap CI-07, UX-C14 |
| R-74 | Help and pricing pages | Add small stories: help pages in M4, `/pricing/` in M5. | UX-C15 |

## 4. Decisions that need a stakeholder

These cannot be settled by the engineering team. Full list with defaults and blocking milestones: [04-open-questions](04-open-questions.md).

| ID | Decision | Engineering recommendation | Needed by |
|---|---|---|---|
| OQ-01 | Monetisation: renter pays 2 credits to Show Number (SRS) **vs** lister pays to unlock leads (flow chart) | Renter pays (SRS) for the MVP; the ledger is generic, so lister-pays can be added later | M4 |
| OQ-29 | Login email: field-level encrypted with a blind index (baseline) **vs** plaintext under KMS storage encryption with compensating controls | Plaintext + compensating controls. All five authors who touched it converged on this, because allauth's `EmailAddress` table is not swappable, so encrypting `User.email` alone protects little | M1 |
| OQ-33 | Launch markets, hosting region(s), data residency | Needed first: drives currency, gateways (Razorpay?), privacy law (GDPR / DPDP), SMS rules | M0 |
| OQ-49 | Product Owner with acceptance authority | Must exist before M0 starts | M0 |
| UX-C13 | "Logout" (SRS) vs "Log out" (UX copy) | "Log out" (verb form for an action) | M1 |
| OQ-50 | Launch hosting target: which PaaS or self-hosted option (ADR-0014) | A PaaS (Render) for the pilot; Kamal on ≥ 2 hosts + managed Postgres for cost-optimised production | Before M7 |
| OQ-51 | Managed Postgres provider (must have PostGIS, pg_trgm, PITR, region per OQ-33) | The PaaS's own if it has PostGIS, otherwise an external managed Postgres | Before M7 |
| OQ-52 | S3-compatible object storage provider | Cloudflare R2 (no egress fees) | M2 |
| OQ-53 | Transactional email provider | Postmark or Mailgun via Anymail | M1 |
| OQ-54 | Cloudflare in front (CDN, WAF, DDoS) | Yes, on every target | Before M7 |
