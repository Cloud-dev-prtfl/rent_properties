# ADR-0014: Portable hosting on PaaS or a self-hosted VPS

Replaces the AWS ECS Fargate + Terraform target (ADR-0008). The application must deploy, unchanged, to a PaaS (Render, Railway, Heroku, Fly.io) **or** to self-hosted servers (Docker Compose, Kamal or Coolify on Hetzner, on-prem or any VPS).

Status: Draft v0.1 (2026-10-27)

| | |
|---|---|
| Decision status | **Accepted** (client decision, 2026-10-27) |
| Date | 2026-10-27 |
| Deciders | Client / Product Owner; Tech Lead |
| Consulted | Security, Platform |
| Supersedes / superseded by | **Supersedes [ADR-0008](0008-aws-ecs-fargate-terraform.md)**. Amends [ADR-0010](0010-field-level-pii-encryption-blind-indexes.md) (key custody) and [ADR-0009](0009-s3-direct-upload-async-image-processing.md) (storage provider) |
| Requirements | SRS §10.1 Cloud Native (NFR-SCAL-01), §8.3 Availability (NFR-AVAIL-*), §9.1 Data Encryption (NFR-SEC-01) |
| Gap / open question | OQ-33 (markets/region), new OQ-50…OQ-54 |
| Related | [Hosting and deployment guide](../architecture/05-hosting-and-deployment.md), [`deploy/`](../../deploy/README.md), register §2.2 |

## Context and problem statement

The client does not want to commit to AWS, and deployment is deferred. Hosting must stay open between two families, which may be used at different stages (for example a PaaS for the pilot and a VPS later, or the reverse):

- **PaaS:** Render, Railway, Heroku, Fly.io. The platform runs containers, routes HTTPS, injects `PORT` and add-on URLs, and offers managed Postgres and Redis.
- **Self-hosted:** Docker Compose, Kamal 2 or Coolify on a VPS or on-prem host. We operate the proxy, database, backups and patching.

## Decision drivers

- One codebase and **one container image** for every target; no per-platform code paths.
- Keep the guarantees the design depends on: PostgreSQL + PostGIS + pg_trgm, row locks for credits, Valkey/Redis for cache and broker, object storage for photos, transactional email.
- Stay 12-factor: all configuration through environment variables, logs to stdout, stateless web processes, migrations as a release step.
- Avoid lock-in: no cloud SDK calls outside adapters.

## Decision outcome

**The application is platform-neutral, and each target is described by a declarative manifest in the repository.**

### Runtime contract (what every target must provide)

| Need | Contract | PaaS | Self-hosted |
|---|---|---|---|
| Container image | `docker/Dockerfile` (last stage `runtime`) | Built by the platform or pushed | Built locally or pushed to a registry |
| Processes | `bin/web`, `bin/worker`, `bin/beat` (**exactly one**), `bin/release` | Procfile / `render.yaml` / `fly.toml` / `heroku.yml` | `compose.prod.yaml` / Kamal roles / Coolify |
| Release step | `bin/release` = `manage.py release` (migrations under a PostgreSQL advisory lock) | Heroku `release`, Render `preDeployCommand`, Fly `release_command` | Compose `release` one-shot; Kamal/Coolify `RELEASE_ON_START=true` |
| HTTP port | `$PORT`, default 8000 | Injected | 8000 behind the proxy |
| TLS + routing | Terminated upstream; `X-Forwarded-Proto` trusted (`FORWARDED_ALLOW_IPS`) | Platform router | Caddy, kamal-proxy or Traefik (Coolify) |
| Health checks | `/healthz` (liveness), `/readyz` (DB + cache + broker); answered before host checks | Platform checker | Proxy health check |
| PostgreSQL 17 + PostGIS + pg_trgm | `DATABASE_URL` (+ `DATABASE_SSLMODE=require` across networks) | Managed Postgres **with PostGIS** | Container with WAL archiving, or an external managed Postgres (recommended) |
| Redis/Valkey | `REDIS_URL` (or `CACHE_URL` + `CELERY_BROKER_URL`); `maxmemory-policy noeviction` when shared | Key-value add-on | Valkey container with AOF persistence |
| Object storage (photos, private docs; M2) | S3-compatible API via django-storages (endpoint, bucket, keys) | External: Cloudflare R2, Backblaze B2, AWS S3, DO Spaces | Same, or Hetzner Object Storage; SeaweedFS/MinIO only for small installs |
| Email | `EMAIL_URL` (SMTP) or an Anymail provider (Postmark, Mailgun, Brevo, SES) | Provider | Provider (never self-run SMTP: deliverability) |
| Secrets | Environment variables | Platform secret store / env groups | `.env.prod` (root-only file), `.kamal/secrets`, Coolify secrets |
| Client IP | `TRUSTED_PROXY_COUNT` or `CLIENT_IP_HEADER` | Router = 1 hop; Fly `Fly-Client-IP` | Proxy = 1 hop; Cloudflare `CF-Connecting-IP` |
| CDN / WAF / DDoS | Cloudflare in front (recommended for both) | Optional | Strongly recommended |
| Scheduled jobs | Celery beat (not platform cron), so schedules are code-reviewed and identical everywhere | Same | Same |
| Observability | stdout JSON logs, Sentry (or GlitchTip), OpenTelemetry OTLP to any backend, external uptime monitor on `/readyz` | Log drains | Docker logs → Vector/Loki or a hosted backend |

### AWS service mapping (how to read the older documents)

| AWS baseline (ADR-0008 era) | Portable replacement |
|---|---|
| ECS Fargate services `web`, `worker`, `beat`; one-off migrate task | Platform processes / compose services / Kamal roles running `bin/*` |
| ALB + target-group health checks | Platform router or Caddy/kamal-proxy/Traefik with `/healthz` |
| CloudFront (static) | WhiteNoise (hashed, pre-compressed) + optional Cloudflare CDN |
| CloudFront + S3 (media), presigned POST | S3-compatible object storage (R2, B2, Spaces, Hetzner, S3) with presigned POST |
| RDS PostgreSQL Multi-AZ, PITR, read replica | Managed Postgres with PostGIS (HA/PITR per plan) **or** self-hosted Postgres + WAL-G/pgBackRest; replica optional |
| ElastiCache Valkey (two clusters: cache LRU, broker noeviction) | One Valkey/Redis with `noeviction` and TTL on every cache key (two instances where the platform allows) |
| Secrets Manager, KMS envelope keys | Platform env secrets; field-encryption keyring from env (see "Key custody") or HashiCorp Vault/OpenBao |
| WAF managed rules | Cloudflare WAF + app-level rate limits |
| CloudWatch logs, metrics, alarms | stdout logs + platform log drains or Loki/Grafana; OTel metrics; Sentry; uptime monitor |
| Terraform | Declarative manifests in the repo (`render.yaml`, `fly.toml`, `heroku.yml`, `deploy/kamal/deploy.yml`, `deploy/compose/compose.prod.yaml`); Terraform/Ansible optional for VPS provisioning |
| `aws ecs run-task` (ops commands) | `render ssh` / `heroku run` / `fly ssh console` / `kamal app exec` / `docker compose exec` |

### Key custody for field-level encryption (amends ADR-0010)

Without a managed KMS, the keyring is supplied as secrets: `FIELD_ENCRYPTION_KEYS` (JSON `{"<version>": "<base64 32-byte key>"}`), `FIELD_ENCRYPTION_ACTIVE_KEY` and `BLIND_INDEX_KEY`. The ciphertext format (`enc:v1:<key_version>:…`) and rotation by adding a new version are unchanged. Keys live only in the platform secret store or root-only files, never in the image, the repository or the database. If a client requires an HSM or KMS later, the keyring adapter can load keys from Vault/OpenBao or a cloud KMS without a data migration. This is implemented in M1.

### Consequences

- **Positive:** no lock-in; the same image runs on 7 targets; lower cost at MVP scale; a simpler mental model (processes + URLs).
- **Negative:**
  - Platform features we planned to lean on now need explicit choices: HA Postgres, PITR, WAF, KMS.
  - A single VPS has **no redundancy**, so it cannot meet 99.9 % on its own.
  - Self-hosting moves backups, patching and incident response onto the team.
  - Some PaaS Postgres plans may lack PostGIS (a hard requirement), so check before choosing.
- **Neutral / follow-on:** the AWS-specific runbook commands, alarms and sizing in older docs must be rewritten for the chosen target before M7 (register §2.2).

### Confirmation (done 2026-10-27, locally)

- The production image ran as the self-hosted stack (`deploy/compose/compose.prod.yaml` with Caddy, HTTPS on `localhost`). The release step applied migrations under the lock, `/readyz` was green, worker and beat ran, the nightly backup wrote a dump, processes ran as non-root, and logs were JSON.
- PaaS simulation: the same image bound to an injected `PORT`, answered `/healthz` for an internal Host header over HTTP, honoured `X-Forwarded-Proto`, redirected plain HTTP, and took the release ID from `RENDER_GIT_COMMIT`.
- Tests cover client-IP resolution, health checks before host validation, the release command, `REDIS_URL` fallback and platform release IDs.
- **Not yet validated against live platforms:** `render.yaml`, `fly.toml`, `heroku.yml` and the Kamal config were written against each platform's documented schema but have not been deployed. Validate them at the first deployment.

## Pros and cons of the options

- **AWS ECS + Terraform (ADR-0008):** the strongest managed guarantees, but lock-in, cost and operational complexity the client does not want now.
- **PaaS only:** the fastest path, but ties the product to one vendor's pricing and limits.
- **Self-hosted only:** the cheapest, but the most operational burden, and HA needs multiple hosts.
- **Portable (chosen):** slightly more care in the app (contracts above), and it keeps every option open.

## Deviations from the SRS

- **§10.1 "Cloud Native … Infrastructure as Code (e.g. Terraform or CloudFormation)":** satisfied in intent through declarative, versioned deployment manifests and containerised, horizontally scalable processes. Terraform is no longer mandatory. **Deviation from SRS:** the cloud-native managed-service stack is not assumed.
- **§9.1 "AES-256 at rest":** still required. On PaaS and managed databases it comes from provider storage encryption. On self-hosted servers it needs **full-disk encryption** (LUKS) on database and backup volumes, plus encrypted off-host backups. Field-level encryption is unchanged.
- **§8.3 availability:** 99.9 % requires at least 2 web/worker instances and an HA (or quickly restorable) database, whichever target is chosen.

## Follow-ups

- Choose the launch target (OQ-50) and record it in a short ADR; then rewrite the runbooks and alerts for it (register H-08).
- M2: S3-compatible storage settings (`STORAGE_*` env vars) and a presigned-POST test against SeaweedFS.
- M1: env-supplied field-encryption keyring.
- Before M7: managed Postgres with PostGIS + PITR **or** WAL-G on the VPS; restore drill on the chosen target; Cloudflare in front.
