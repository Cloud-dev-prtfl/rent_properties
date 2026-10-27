# Milestones and Backlog

The build plan we will execute chunk by chunk. Each milestone (M0–M7, plus Post-MVP) lists its goal, scope, epics and user stories with acceptance criteria, deliverables, exit criteria with a demo script, and a relative size.

Status: Draft v0.1 (2026-10-21)

Related: [01 Development Approach](01-development-approach.md) · [04 Testing Strategy](04-testing-strategy.md) · [05 DoD & Workflow](05-definition-of-done-and-workflow.md) · [UX & Page Inventory](../ux/01-ux-and-page-inventory.md)

---

## 0. How to read this backlog

- **Story IDs:** `US-<milestone><nn>`. Examples: `US-012` is M0 story 12; `US-405` is M4 story 05; `US-9nn` is Post-MVP.
- **Epic IDs:** `EP-<milestone>.<n>`.
- **Sizes:** stories are **S** ≤ 1 day, **M** 2–3 days, **L** 4–5 days (consider splitting). Milestones are **S** ≤ 1 iteration, **M** about 1 iteration, **L** 1.5–2 iterations ([01 §5](01-development-approach.md#5-chunk-sizing)).
- **Acceptance criteria** here are summaries. During refinement each is expanded to Given/When/Then and automated ([05 §2](05-definition-of-done-and-workflow.md#2-definition-of-ready-dor)).
- **Stretch** stories are pulled in only if the milestone goal is already met.
- Statuses, model fields and URL details are **indicative**. The data-model, architecture and security docs are authoritative. If they differ, those docs win and this file is updated.

### 0.1 Requirement reference key

These IDs follow the catalog naming scheme. **If the requirements catalog (`docs/requirements/`) numbers an item differently, the SRS § column is the binding reference.** In that case, update this table in a single PR.

| ID | SRS § | Requirement (short) |
|---|---|---|
| FR-AUTH-01 | 3.1 | Email/password sign-up with real-time validation (format, strength, uniqueness) |
| FR-AUTH-02 | 3.1 | Social sign-on, Google/Apple (optional) |
| FR-AUTH-03 | 3.2 | Verification by email confirmation or phone OTP; unverified accounts restricted |
| FR-AUTH-04 | 3.3 | **CRITICAL** 10 promo credits granted once, logged with metadata |
| FR-AUTH-05 | 3.4 | Secure login, hashing, session management, forgot password |
| FR-AUTH-06 | HLRD intro | RBAC for three core user types |
| FR-LIST-01 | 4.1 | Multi-step submission, drafts, client-side validation |
| FR-LIST-02 | 4.2 | Required fields; images min 3 / max 20, ≤ 5 MB, aspect ratio, thumbnails |
| FR-LIST-03 | 4.3 | **CRITICAL** AgentListed/OwnerListed tag; changes only via admin review |
| FR-LIST-04 | 4.4 | Listing management (view/edit/mark rented/unlist) plus real-time metrics |
| FR-LIST-05 | 4.5 | Search & filter: location, price, type, tag; geospatial, multi-select, sort, fuzzy |
| FR-CRED-01 | 5.1 | **CRITICAL** "Show Number" visibility rules and cost display |
| FR-CRED-02 | 5.2 | **CRITICAL** Atomic credit check (≥ 2) |
| FR-CRED-03 | 5.3 | **CRITICAL** Deduct 2 credits; immutable ledger entry |
| FR-CRED-04 | 5.4 | Contact display; available again from history at no cost |
| FR-CRED-05 | 5.5 | Automated reveal email (receipt plus lead record) |
| FR-CRED-06 | 5.6 | Insufficient-credit notification with a link to Purchase Credits |
| FR-PAY-01 | 6.1 | Purchase Credits reachable from the profile dropdown; fast funnel |
| FR-PAY-02 | 6.2 | Credit packages, volume discounts, localised currency |
| FR-PAY-03 | 6.3 | ≥ 2 gateways, tokenisation, webhooks |
| FR-PAY-04 | 6.4 | **CRITICAL** Allocation within 5 s after verified confirmation |
| FR-PAY-05 | 6.5 | Filterable transaction history |
| FR-PROF-01 | 7, 7.1 | **CRITICAL** Profile icon at top right; dropdown shows name/email and balance |
| FR-PROF-02 | 7.2 | **CRITICAL** Dropdown tabs: Profile (edit, two-step sensitive changes, preferences), My Properties, Purchase Credits |
| FR-PROF-03 | 7.3 | Logout terminates the server session and invalidates tokens |
| NFR-PERF-01 | 8.1 | Search and credit transactions: < 500 ms standard, < 1000 ms peak |
| NFR-PERF-02 | 8.2 | 1,000 concurrent credit transactions/sec without inconsistency |
| NFR-AVAIL-01 | 8.3 | Restore testing, incident runbooks (plus proposed SLA/RPO/RTO) |
| NFR-SEC-01 | 9.1 | TLS 1.2+, AES-256 at rest, PII tokenised/pseudonymised |
| NFR-SEC-02 | 9.2 | Credit integrity: immutable linked audit trail, automated audits |
| NFR-SEC-03 | 9.3 | PCI DSS through gateways; no raw card data |
| NFR-SCAL-01 | 10.1 | Cloud-native, horizontally scalable, IaC |
| NFR-MAINT-01 | 10.2 | Best practices, mandatory reviews, ≥ 90 % unit+integration coverage |
| NFR-UX-01 | 11.1 | Persistent credit balance in header |
| NFR-UX-02 | 11.1 | Non-modal reveal confirmation toast (exact copy) |
| NFR-UX-03 | 11.1 | Distinct AgentListed/OwnerListed styling |
| NFR-UX-04 | 11.2 | Fluid profile dropdown (click/touch, instant, no layout shift) |
| NFR-UX-05 | 11.2 | Guided listing: progress indicator, inline validation |
| NFR-UX-06 | 11.2 | Mobile-first |
| NFR-A11Y-01 | 12 | WCAG 2.1 AA |
| DIA-OPS-01 | Diagram | Ops console: job monitoring, listing moderation, fraud review |
| DIA-KYC-01 | Diagram | Verification API: owner identity, listing checks, KYC docs, ownership proofs |
| DIA-LEAD-01 | Diagram | Lead/inquiry forms; lister notified of new lead; lister-pays unlock |

### 0.2 Milestone overview

| Milestone | Goal (one line) | Size | Critical path |
|---|---|---|---|
| [M0](#m0--foundations--walking-skeleton) | Deployable, observable, tested empty product on `dev` | M | Yes |
| [M1](#m1--identity--accounts) | Users can register, verify, log in/out, manage their profile; RBAC in place | M | Yes |
| [M2](#m2--listings) | Listers can publish and manage high-quality listings | L | Yes |
| [M3](#m3--search--discovery) | Renters can find listings fast and save them | M | No (parallel with M4) |
| [M4](#m4--credits--contact-reveal) | The CRITICAL credit path works end-to-end and holds under load | L | Yes |
| [M5](#m5--payments) | Users can buy credits with two gateways; credits allocated in ≤ 5 s | L | Yes |
| [M6](#m6--ops-console--moderation) | Staff can moderate, review tag changes, handle fraud and audit the ledger; listers see analytics | M | Partly |
| [M7](#m7--hardening--launch-readiness) | Verified, secure, accessible, recoverable production launch | L | Yes |
| [Post-MVP](#post-mvp-backlog) | Prioritised after launch | — | — |

---

## M0 — Foundations & Walking Skeleton

**Goal:** Every later story only adds behaviour. M0 builds the repo, toolchain, CI/CD, infrastructure, observability, design-system shell and test harness, deployed end-to-end to `dev`.
**Size:** M · **Depends on:** — · **Requirements:** NFR-SCAL-01, NFR-MAINT-01, NFR-SEC-01 (transport), NFR-A11Y-01 (baseline), NFR-UX-06

**Scope in:** repo layout, uv, quality tooling, docker compose, settings split, `apps.core` foundations, custom User model stub, Celery/beat, structlog/Sentry/OTel, health endpoints, Tailwind + HTMX + Alpine base layout and design tokens, i18n setup, security headers, Terraform skeleton and `dev` environment, CI/CD to `dev`, test harnesses (pytest, Playwright, axe, k6), ADR process, the concurrency spike.
**Scope out:** any business feature; staging (provisioned at the end of M1); prod (M5 rehearsal / M7).

> **Hosting change (2026-10-27, [ADR-0014](../adr/0014-portable-hosting-paas-and-self-hosted.md)):** US-011 (Terraform on AWS) is **replaced** by declarative deployment manifests for PaaS and self-hosted targets (`render.yaml`, `fly.toml`, `heroku.yml`, `Procfile`, `deploy/compose`, `deploy/kamal`). These are done and the self-hosted stack was verified locally. US-010's deploy-to-`dev` steps, the hosted `dev` environment and the RDS part of US-012 are **deferred** until a target is chosen (OQ-50). CI currently runs checks, tests, the image build and a vulnerability scan. Status: M0 done locally on 2026-10-27.

### Epics and stories

**EP-0.1 Repository & toolchain**

| ID | Story | Acceptance criteria (summary) | Req | Size |
|---|---|---|---|---|
| US-001 | As a developer, I want a bootstrapped repo with the canonical layout, so that everyone builds on the same structure. | `pyproject.toml` (uv, Python 3.13, Django 5.2 LTS, exact pins), `manage.py`, `config/` (settings `base/local/test/production`, `urls`, `wsgi`, `asgi`, `celery`), `apps/`, `templates/`, `static/`, `infra/terraform/`, `docker/`, `docs/`, `tests/`. `uv sync && make check` passes on a clean clone. README quick start. | NFR-MAINT-01 | S |
| US-002 | As a developer, I want linting, formatting, typing and security checks enforced, so that quality is automatic. | ruff (lint + format), mypy with django-stubs, djLint (templates), bandit, pip-audit, gitleaks, and `makemigrations --check` wired into pre-commit and CI. Violations fail CI. Config as in [03](03-engineering-standards.md). | NFR-MAINT-01 | S |
| US-003 | As a developer, I want a one-command local environment, so that onboarding takes minutes. | `docker compose up` starts web (Gunicorn), worker, beat, PostgreSQL 17 + PostGIS, Redis/Valkey, Nginx (static/media proxy), Mailpit, and S3-compatible storage (choice recorded in an ADR). Healthy within 5 min on a fresh machine. `make seed` works. | NFR-SCAL-01 | M |
| US-004 | As an operator, I want 12-factor configuration, so that one image runs in every environment. | All settings come from environment variables. Secrets are never in the repo. `production.py` fails fast if a required variable is missing. `DEBUG` cannot be enabled in production settings (test asserts it). | NFR-SEC-01 | S |
| US-016 | As a developer, I want a custom `accounts.User` model before the first migration, so that we never need a painful mid-project user-model swap. | `AUTH_USER_MODEL = "accounts.User"` with email as the identifier, UUID `public_id`, and timestamps. It is the first migration. Argon2id is the default hasher, with bcrypt kept as a fallback hasher. | FR-AUTH-05 | S |

**EP-0.2 Core platform**

| ID | Story | Acceptance criteria (summary) | Req | Size |
|---|---|---|---|---|
| US-005 | As a developer, I want shared base models and infrastructure in `apps.core`, so that every app uses one convention. | `TimeStampedModel`, UUID public-id mixin, `core.OutboxMessage` + dispatcher task (idempotent, retries with backoff), `core.AuditLog` model + `audit_log_record()` service, request-ID middleware, domain error base class. Unit tests ≥ 95 %. | NFR-MAINT-01, NFR-SEC-02 | M |
| US-007 | As a developer, I want Celery and beat configured, so that background work is reliable. | `config/celery.py`, django-celery-beat, named queues (`default`, `critical`, `email`, `media`, `analytics`, `audit`), a base task with `acks_late`, time limits and retries. Sample task runs in compose and on `dev`. | NFR-SCAL-01 | S |
| US-006 | As an operator, I want logs, errors and traces from day one, so that incidents are diagnosable. | structlog JSON with `request_id`, `trace_id` and `user_public_id`; Sentry (PII scrubbing on); OpenTelemetry for Django, psycopg, Celery and Redis; `/healthz` (liveness), `/readyz` (DB + cache + broker); CloudWatch log groups. One request shows the same IDs across all three tools. | NFR-AVAIL-01 | M |
| US-015 | As a security engineer, I want safe HTTP defaults, so that common web attacks are blocked from the start. | HSTS, CSP (no inline scripts; nonce-free strict policy), `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`, secure cookie flags, CSRF failure page, custom 400/403/404/429/500 pages (500 page shows the request ID). ZAP baseline reports no High findings. | NFR-SEC-01 | S |

**EP-0.3 Design system & front-end foundation**

| ID | Story | Acceptance criteria (summary) | Req | Size |
|---|---|---|---|---|
| US-008 | As a user, I want a consistent, accessible page shell, so that every page looks and behaves the same. | Tailwind build (pinned standalone CLI), design tokens as in [UX §9](../ux/01-ux-and-page-inventory.md#9-design-tokens), `base.html` with skip link, landmark regions, header shell (logo, nav, placeholders for the balance badge and profile button), footer, toast regions (`aria-live`). HTMX 2 and Alpine 3 (CSP build) vendored with exact versions. axe: 0 serious/critical. Works at 360 px. | NFR-UX-06, NFR-A11Y-01 | M |
| US-009 | As a future international user, I want the app built for translation from the start, so that new languages need no code changes. | `LocaleMiddleware`, `i18n_patterns(prefix_default_language=False)`, all template strings wrapped, `makemessages` runs in CI, `USE_TZ=True`, `<html lang dir>` set from the active language. | NFR-UX-06 | S |

**EP-0.4 Infrastructure & delivery**

| ID | Story | Acceptance criteria (summary) | Req | Size |
|---|---|---|---|---|
| US-011 | As an operator, I want infrastructure as code, so that environments are reproducible. | Terraform modules for VPC, ECS Fargate (web/worker/beat), ALB, RDS PostgreSQL 17 + PostGIS, ElastiCache, S3 (public media prefix and private docs bucket), CloudFront, WAF (managed rules), ECR, Secrets Manager, KMS, CloudWatch. Remote state with locking. `dev` applied. `terraform plan` shows no drift. | NFR-SCAL-01 | L |
| US-010 | As a developer, I want CI/CD to `dev`, so that every merge is verified and deployed. | GitHub Actions: lint/type, tests with PostGIS + Redis service containers, coverage, build, image scan, push to ECR, a one-off migration task, rolling deploy to `dev` with health-check rollback, then ZAP baseline. PR pipeline ≤ 10 min. | NFR-MAINT-01, NFR-SCAL-01 | M |
| US-013 | As QA, I want test harnesses ready, so that each feature ships with tests. | pytest-django, factory_boy, pytest-xdist, coverage config (gates per [04 §14](04-testing-strategy.md#14-coverage-gates)), Playwright smoke test of the shell page, axe check helper, k6 script skeleton, Lighthouse CI budget file. | NFR-MAINT-01, NFR-A11Y-01 | M |
| US-014 | As the team, I want an ADR process and seed ADRs, so that decisions are traceable. | `docs/adr/` with template and index. Seed ADRs: Django monolith; server-side sessions instead of JWT; PostgreSQL row-level concurrency instead of Kafka; HTMX/Alpine instead of SPA; feature-flag mechanism; local S3 emulator. | NFR-MAINT-01 | S |

**EP-0.5 Risk spike**

| ID | Story | Acceptance criteria (summary) | Req | Size |
|---|---|---|---|---|
| US-012 | As the tech lead, I want to prove the debit design can sustain 1,000 TPS without inconsistency, so that we confirm (or change) the architecture before building on it. | Timeboxed to 3 days. Prototype wallet table with `CHECK (balance >= 0)`, a conditional `UPDATE … WHERE balance >= 2 RETURNING`, and a ledger insert. k6 at 1,000 req/s for 5 min on dev-sized RDS: error rate < 0.1 %, p95 recorded, 0 negative balances, ledger sum equals balance. A hot-wallet test (200 concurrent requests on one wallet) gives exactly ⌊balance/2⌋ successes. Results go into an ADR. The prototype is thrown away or kept as a benchmark. | NFR-PERF-02, NFR-SEC-02 | M |

### Deliverables
Repo with toolchain; docker compose stack; `dev` environment on AWS through Terraform; CI/CD pipeline; base layout and tokens; core app; observability; test harnesses; seed ADRs; spike report.

### Exit criteria and demo script
1. Open a trivial PR (copy change). CI runs lint, type, test, build and scan, all green in ≤ 10 min.
2. Merge. The pipeline deploys to `dev` automatically. Open `https://<dev-domain>/`: the shell page renders with header, footer and skip link. Keyboard Tab shows a visible focus ring.
3. `GET /readyz` returns 200 with DB, cache and broker checks.
4. Trigger the sample Celery task from the shell. Show the log line in CloudWatch and the trace in OTel/Sentry with the same `request_id`.
5. Show the spike ADR: 1,000 TPS result, p95, and the zero-inconsistency proof.
6. Show the axe report (0 serious/critical) and the ZAP baseline (0 High).

---

## M1 — Identity & Accounts

**Goal:** Users can register, verify, log in and out securely, and manage their profile. The header and profile dropdown shell and the RBAC groups are in place.
**Size:** M · **Depends on:** M0 · **Requirements:** FR-AUTH-01/02/03/05/06, FR-PROF-01/02/03, NFR-SEC-01, NFR-UX-04, NFR-A11Y-01

**Scope in:** django-allauth email login with mandatory verification, phone OTP (Twilio Verify), server-side sessions (Redis-backed `cached_db`), logout everywhere, password reset, profile and two-step sensitive changes, notification preferences, RBAC groups, staff MFA, header/dropdown shell (balance placeholder), anti-abuse basics, auth audit events, `staging` environment.
**Scope out:** promo credit grant (M4, because the wallet doesn't exist yet; users verified in M1 are backfilled by US-403); user MFA for renters and listers (Post-MVP); Social SSO (stretch, otherwise Post-MVP); account closure (Post-MVP, pending OQ).

**EP-1.1 Registration & verification**

| ID | Story | Acceptance criteria (summary) | Req | Size |
|---|---|---|---|---|
| US-101 | As a visitor, I want to sign up with email and password and get real-time feedback, so that I can register without trial and error. | Fields: name, email, password, confirm, terms checkbox. HTMX validation on blur (debounced 400 ms) for email format and uniqueness, and password strength (Django validators: min length 12, common-password, similarity, numeric-only). The uniqueness check is rate-limited (e.g. 10/min/IP) to limit enumeration. Server-side validation is authoritative. Errors are linked to fields (`aria-describedby`). Account created as **unverified**. | FR-AUTH-01, NFR-A11Y-01 | M |
| US-102 | As a new user, I want to verify my email, so that my account is activated. | allauth mandatory verification by code or link (single-use, expires in 24 h — **Assumption**). Resend has a 60 s cooldown. On success the state becomes verified and an AuditLog entry is written. The verification email is translatable and sent through anymail. | FR-AUTH-03 | M |
| US-103 | As a new user, I want to verify my phone by OTP as an alternative, so that I can activate without email access. | Twilio Verify: 6-digit code, 10-minute expiry, 5 attempts, 60 s resend cooldown, rate limits per phone and per IP. The phone is normalised to E.164 and must be unique among verified users. Verifying either email or phone activates the account (SRS "email **or** phone" — **Assumption** pending OQ). | FR-AUTH-03 | M |
| US-104 | As the business, I want unverified accounts restricted from transactional actions, so that spam and promo abuse are limited. | A `verified_required` decorator/mixin protects listing creation, reveal, purchase and saved properties. Unverified users get a 403 page explaining why, with a "Verify now" CTA. A test matrix covers every protected URL. | FR-AUTH-03, FR-AUTH-06 | S |
| US-105 | As the business, I want basic anti-abuse controls at signup, so that promo credits are not farmed. | Disposable-email domain blocklist (updatable). Signup rate limit per IP. Optional CAPTCHA switch (feature flag) for abuse spikes. Normalised-email uniqueness (case-insensitive). AuditLog for blocked attempts. | FR-AUTH-04 (abuse), NFR-SEC-01 | S |

**EP-1.2 Login, sessions, logout**

| ID | Story | Acceptance criteria (summary) | Req | Size |
|---|---|---|---|---|
| US-106 | As a user, I want to log in securely, so that I can access my account. | Email + password. Generic error on failure (no account enumeration). allauth rate limits on login failures. Session key rotated on login. Cookies: `Secure`, `HttpOnly`, `SameSite=Lax`. Idle timeout 2 weeks with "remember me", otherwise browser session (**Assumption**). `next` redirect validated against allowed hosts. | FR-AUTH-05 | M |
| US-107 | As a user, I want logout to fully end my session, so that nobody can reuse it. | POST-only logout (CSRF). The server-side session is deleted. Response sends `Clear-Site-Data: "cache", "cookies", "storage"`. Back-button after logout shows no private data (`Cache-Control: no-store` on authenticated pages). The Logout control sits at the bottom of the dropdown. | FR-PROF-03, FR-AUTH-05 | S |
| US-108 | As a user, I want to see my active sessions and sign out of others, so that I control access to my account. | allauth `usersessions`: list devices/IPs/last seen; "Sign out other sessions". Password change and reset invalidate all other sessions. | FR-PROF-03, NFR-SEC-01 | S |
| US-109 | As a user, I want a forgot-password flow with a time-limited link, so that I can recover access safely. | The reset email is sent only if the account exists, but the response is always the same. Link is single-use and expires in 1 h (**Assumption**; Django's default is longer). Reset invalidates all sessions and sends a "password changed" notice. | FR-AUTH-05 | S |

**EP-1.3 Profile & preferences**

| ID | Story | Acceptance criteria (summary) | Req | Size |
|---|---|---|---|---|
| US-110 | As a user, I want to view and edit my name and phone, so that my details are current. | Profile page. Inline validation. Changing the phone requires OTP before it takes effect. Changes are audited. | FR-PROF-02 | S |
| US-111 | As a user, I want changing my email or password to be a secure two-step process, so that my account can't be hijacked. | Re-authentication required (allauth reauthenticate, 10-minute window). New email is verified before it replaces the old one, and the old address is notified. Password change requires the current password and notifies by email. | FR-PROF-02, NFR-SEC-01 | M |
| US-112 | As a user, I want to manage my notification preferences, so that I only receive the emails I want. | `NotificationPreference`: promotional alerts opt-in (default **off** — **Assumption**, GDPR-safe), product updates. Transactional emails (verification, receipts, reveal confirmation) are always on and labelled as such. Unsubscribe link in promotional emails. | FR-PROF-02 | S |

**EP-1.4 RBAC & staff**

| ID | Story | Acceptance criteria (summary) | Req | Size |
|---|---|---|---|---|
| US-113 | As the business, I want a defined role model, so that authorisation is consistent. | Roles: **Renter** and **Lister** are capabilities of any verified user (one account can do both; the lister type is per listing via the tag). **Staff** sub-roles are Django groups — Moderator, Support, Finance, Superadmin — created by a data migration with explicit permissions. Permission matrix documented. Tests cover every role × protected view. **Deviation from SRS:** "three core user types" is interpreted as Renter / Lister / Staff (GAP: undefined in the SRS). | FR-AUTH-06 | M |
| US-114 | As the business, I want staff accounts protected by MFA, so that the console can't be taken over with a stolen password. | allauth MFA (TOTP plus recovery codes) mandatory for any `is_staff` user before admin/ops access. Admin moved off `/admin/` to `/ops/admin/`. Enforced on all internet-facing environments. User MFA for renters/listers stays Post-MVP. | NFR-SEC-01, DIA-OPS-01 | S |
| US-115 | As an auditor, I want security-relevant account events recorded, so that incidents can be investigated. | AuditLog for signup, verification, login success/failure, logout, password/email/phone change, session revocation, role change. No secrets or PII values in the payload (IDs only). | NFR-SEC-01 | S |

**EP-1.5 Header & navigation shell**

| ID | Story | Acceptance criteria (summary) | Req | Size |
|---|---|---|---|---|
| US-116 | As a logged-in user, I want a profile icon at the top right that opens my account menu, so that account actions are always one click away. | Disclosure pattern as in [UX §5](../ux/01-ux-and-page-inventory.md#5-global-header-and-profile-dropdown). Shows name and email, a balance slot (shows "—" until M4 behind a flag), then Profile, My Properties, Purchase Credits, Transaction History, Saved, Ops (staff only) and Logout at the bottom. Server-rendered so it opens instantly. Esc closes and returns focus. Works by click, touch and keyboard. No layout shift. Touch targets ≥ 44 × 44 px. | FR-PROF-01, FR-PROF-02, NFR-UX-04 | M |
| US-117 | As a visitor, I want clear Log in / Sign up entry points, so that I can join easily. | Anonymous header shows "List your property", "Log in" and "Sign up". Mobile layout per the UX spec. | NFR-UX-06 | S |

**EP-1.6 Environments & stretch**

| ID | Story | Acceptance criteria (summary) | Req | Size |
|---|---|---|---|---|
| US-118 | As the team, I want a `staging` environment, so that stakeholders can review stable builds. | Same Terraform modules. Image promoted by digest. Basic access control (WAF IP allowlist or SSO). Synthetic data only. SES/Twilio limited to allowlisted recipients. | NFR-SCAL-01 | M |
| US-119 *(stretch)* | As a visitor, I want to sign up with Google (and Apple), so that registration is faster. | allauth social providers. Account linked by verified email. Social accounts count as email-verified only if the provider asserts a verified email. Needs the Apple Developer account (long-lead item). Otherwise this moves to Post-MVP US-901. | FR-AUTH-02 | M |

### Deliverables
Auth flows (signup, verify by email/phone, login, logout, reset, reauth); profile and preferences; sessions page; RBAC groups and permission matrix; staff MFA; header/dropdown shell; `staging`; auth E2E journey.

### Exit criteria and demo script
1. On `staging`, sign up with a weak password: real-time feedback appears. Fix it and submit. Try a disposable email: it is blocked.
2. Open the verification email in the allowlisted inbox and verify. Try `/my-properties/new/` before verifying: a 403 explains why.
3. Log in. Open the profile dropdown with the mouse, then with the keyboard (Enter, Tab, Esc returns focus), then on a phone.
4. Change email (reauth, verify new address, old address notified). Change password. Other sessions are signed out.
5. Log out, press Back: no private content. Use "Forgot password" and confirm an expired link is rejected.
6. Log in as Moderator: TOTP enrolment is forced and `/ops/admin/` is reachable. A Renter gets 403 there.
7. Evidence: auth E2E green, coverage ≥ 90 %, axe clean on all auth pages.

---

## M2 — Listings

**Goal:** Verified users can create, draft, publish, edit and manage high-quality listings with validated images, geocoded addresses, an immutable lister tag and encrypted contact data. Each listing has a public detail page.
**Size:** L · **Depends on:** M1 · **Requirements:** FR-LIST-01/02/03/04, FR-CRED-01 (placeholder states), NFR-UX-05, NFR-UX-06, NFR-SEC-01, NFR-A11Y-01

**Scope in:** `listings` app (Property, PropertyImage, PropertyTagChangeRequest), `geo` GeocodingService, multi-step form with drafts, presigned direct-to-S3 uploads and Celery image processing, contact field encryption, My Properties dashboard (metrics placeholders), status transitions, public detail page (Show Number state shell without debit), view-count events, demo/perf seed data.
**Scope out:** search (M3); real reveal (M4); the moderation queue UI (M6 — M2 provides a minimal admin approval action for tag changes); KYC/ownership proofs (Post-MVP; the private bucket and hooks exist).

**EP-2.1 Property model & lifecycle**

| ID | Story | Acceptance criteria (summary) | Req | Size |
|---|---|---|---|---|
| US-201 | As a developer, I want the Property aggregate with a guarded status lifecycle, so that listings can't reach invalid states. | Property with UUID `public_id`, owner, `lister_tag` (AgentListed/OwnerListed), type, title, description, rent (integer minor units + ISO-4217 currency), address fields, PostGIS `Point` (SRID 4326), encrypted contact phone/email, status (indicative: DRAFT → PUBLISHED ↔ UNLISTED; PUBLISHED → RENTED; any → SUSPENDED by staff), `published_at`. Transitions go only through services; invalid transitions raise `InvalidStateTransitionError`. DB check constraints on required published fields. | FR-LIST-02, FR-LIST-04 | M |
| US-202 | As a lister, I want only my own listings editable by me, so that nobody can tamper with them. | All lister views scope by `owner=request.user` in selectors. Accessing another user's listing returns 404 (not 403, to avoid leaking existence). Automated IDOR tests for every lister URL. | FR-AUTH-06, NFR-SEC-01 | S |

**EP-2.2 Guided multi-step submission with drafts**

| ID | Story | Acceptance criteria (summary) | Req | Size |
|---|---|---|---|---|
| US-203 | As a lister, I want to start a listing and have it saved as a draft automatically, so that I never lose work. | "List your property" creates a DRAFT and redirects to step 1. Each "Next" saves server-side. "Save draft & exit" is available on every step. Drafts are resumable from My Properties. Draft retention 90 days, then a reminder email and deletion (**Assumption**). | FR-LIST-01 | M |
| US-204 | As a lister, I want a clear step-by-step form with progress, so that the task feels manageable. | Six steps: Basics → Location → Details & price → Photos → Contact → Review. Progress indicator per the [UX spec](../ux/01-ux-and-page-inventory.md#8-multi-step-listing-form). Completed steps are navigable. On step change, focus moves to the step heading. A warning appears before leaving with unsaved changes. | FR-LIST-01, NFR-UX-05 | M |
| US-205 | As a lister, I want inline validation before submitting, so that I fix mistakes early. | HTML5 constraints plus Alpine inline messages on blur. The server re-validates everything. On submit failure, an error summary at the top with links to fields gets focus. `aria-invalid` and `aria-describedby` set. Mandatory: address, type, price, description, images (3–20), contact (phone and/or email), tag. | FR-LIST-01, FR-LIST-02, NFR-A11Y-01 | M |
| US-206 | As a lister, I want to choose AgentListed or OwnerListed and understand it is permanent, so that renters can trust the label. | Required radio group (fieldset/legend), with a briefcase icon for Agent and a house icon for Owner. Helper text: "This can't be changed after publishing without a review." No default selection. | FR-LIST-03, NFR-UX-03 | S |
| US-207 | As a lister, I want to enter details and price, so that renters can evaluate the property. | Property type (enumeration, OQ for the final list), monthly rent (> 0, max bound), currency (defaults from the market), optional bedrooms, bathrooms, area (m²/ft² per locale), furnishing, available-from date. **Assumption:** the attributes beyond the SRS minimum are optional (OQ). | FR-LIST-02 | S |
| US-208 | As a lister, I want to provide contact details that default from my profile, so that renters can reach me after paying. | Phone (E.164) and/or email; at least one is required. Prefilled from the profile and editable per listing. Stored with application field-level encryption. **Never rendered** in any HTML/JSON response except to the owner and to users who have revealed it (M4). The tests assert this. | FR-LIST-02, NFR-SEC-01 | M |
| US-209 | As a lister, I want to review everything and publish, so that my listing goes live correctly. | Review page with "Edit" links per section. Publishing validates completeness (including ≥ 3 processed images and geocoded coordinates), sets PUBLISHED and `published_at`, and freezes the tag. Confirmation checkbox: "I am the owner or authorised agent" (**Assumption**). Success page links to the public listing. | FR-LIST-01, FR-LIST-03 | S |

**EP-2.3 Images pipeline**

| ID | Story | Acceptance criteria (summary) | Req | Size |
|---|---|---|---|---|
| US-210 | As a lister, I want to upload photos quickly from my phone, so that I can finish the listing in one go. | Presigned direct-to-S3 upload (private `uploads/` prefix). Client checks type (JPEG/PNG/WebP; HEIC per OQ) and size ≤ 5 MB before upload. Per-file progress and error. Min 3 / max 20 enforced client- and server-side. Keyboard-accessible file picker plus drag-and-drop. Reorder with "Move up/down" buttons (not drag-only). Choose a cover photo. Optional caption used as alt text. | FR-LIST-02, NFR-UX-06, NFR-A11Y-01 | L |
| US-211 | As the platform, I want every image verified and optimised, so that pages are fast and safe. | Celery `media` queue: Pillow verify (rejects non-images and polyglots), size ≤ 5 MB, min resolution 800 × 600 (**Assumption**), aspect ratio between 3:4 and 2:1 (**Assumption**; OQ); otherwise rejected with a clear message. EXIF stripped (including GPS). WebP variants: thumb 400w, card 800w, large 1600w, written to the public media prefix and served through CloudFront. Status PENDING → READY/REJECTED is shown live via HTMX polling (2 s, stops when done). | FR-LIST-02, NFR-PERF-01 | L |

**EP-2.4 Geocoding**

| ID | Story | Acceptance criteria (summary) | Req | Size |
|---|---|---|---|---|
| US-212 | As a lister, I want my address located on a map, so that renters searching by location find my property. | `geo.GeocodingService` (provider-agnostic; Google Maps Platform or Mapbox adapter) geocodes on step submit. Results cached (Redis, 30 days) and rate-limited. The lister confirms or adjusts the pin (map optional; a text address is always shown). Stored as PostGIS Point. If the provider fails, the draft is saved and the lister sees a "We couldn't locate this address yet" message. Publishing is blocked until coordinates exist. | FR-LIST-02, FR-LIST-05 | M |

**EP-2.5 Lister tag governance**

| ID | Story | Acceptance criteria (summary) | Req | Size |
|---|---|---|---|---|
| US-213 | As a lister, I want to request a tag change with a reason, so that I can correct a genuine mistake. | After publishing, the tag field is read-only everywhere (form and service; service-level test). "Request tag change" creates a `PropertyTagChangeRequest` (from, to, reason, optional evidence upload to the private bucket, status PENDING). One open request per property. Lister sees the status. | FR-LIST-03 | M |
| US-214 | As a moderator, I want to approve or reject tag-change requests, so that tags stay truthful. | Minimal Django-admin action in M2 (the full queue UI is in M6). Approval changes the tag in one transaction with an AuditLog entry. Rejection requires a reason. The lister is emailed either way. | FR-LIST-03, DIA-OPS-01 | S |

**EP-2.6 My Properties management**

| ID | Story | Acceptance criteria (summary) | Req | Size |
|---|---|---|---|---|
| US-215 | As a lister, I want a dashboard of my properties, so that I can manage them in one place. | `/my-properties/`: cards or rows with cover, title, status chip, created/published date, and quick actions (Edit, Continue draft, Mark rented, Unlist/Relist, View). Status filter. Metric tiles for views, saves and Show Number clicks per listing (views live from US-218; saves from M3; reveals from M4; "—" until then). Empty state with CTA. | FR-LIST-04, FR-PROF-02 | M |
| US-216 | As a lister, I want to edit a published listing, so that details stay accurate. | All fields except the tag are editable. An address change re-geocodes. The image set must stay 3–20 READY images. Edits are audited (who, when, changed fields). Search cache is invalidated on save (hook ready for M3). | FR-LIST-04 | M |
| US-217 | As a lister, I want to mark a property rented or unlist and relist it, so that renters only see available homes. | Confirmation dialog (`<dialog>`, focus managed). Transitions go through the service. RENTED and UNLISTED listings disappear from public search. The detail page shows "No longer available" (HTTP 200 with banner, `noindex`). Previously revealed contacts stay visible to those renters (M4). | FR-LIST-04 | S |

**EP-2.7 Public listing detail page**

| ID | Story | Acceptance criteria (summary) | Req | Size |
|---|---|---|---|---|
| US-218 | As a renter, I want a rich, fast listing page, so that I can judge a property. | `/properties/<public_id>/<slug>/` (canonical redirect if the slug differs). Accessible gallery (buttons, no autoplay, lightbox `<dialog>`), price, tag badge, key facts, description, map with a text address fallback, lister display name and type, posted date. Show Number area rendered in **state shell** mode (anonymous / unverified / own listing / unavailable) with no debit yet. LCP image prioritised. View events are counted (deduplicated per session per listing per day) into `analytics`. | FR-LIST-04, FR-CRED-01, NFR-UX-03, NFR-PERF-01 | L |
| US-219 | As the team, I want realistic seed data, so that demos and performance tests are meaningful. | `manage.py seed_demo` (about 200 listings with images, idempotent) and `seed_perf` (configurable, default 500k listings and 200k users across synthetic cities). Synthetic data only. | NFR-PERF-01 | M |

### Deliverables
Listing creation and management end-to-end, image pipeline, geocoding adapter, tag governance (request plus minimal approval), detail page, seed commands, Playwright journey "list a property".

### Exit criteria and demo script
1. As a verified user on a phone-sized viewport, click "List your property". Complete Basics, choosing **OwnerListed**, then "Save draft & exit".
2. Open My Properties and resume the draft. Enter an address and confirm the pin. Upload 4 photos, one of them 7 MB: it is rejected inline with a size message. Reorder photos and pick a cover. Processing status turns to READY live.
3. Enter contact details, review and publish. Open the public page in a private window: the contact is **not** in the page source. Show Number displays "Log in to view number".
4. Try to edit the tag: it is read-only. Request a change. As Moderator in `/ops/admin/`, approve it. The badge updates and the AuditLog has the entry.
5. Mark the listing rented: the public page shows "No longer available".
6. Evidence: E2E "list a property" green, IDOR tests green, axe clean on all six form steps, image security tests (EXIF GPS stripped, polyglot rejected).

---

## M3 — Search & Discovery

**Goal:** Renters find relevant listings fast (p95 < 500 ms at standard load) by location, price, type and tag, with fuzzy matching and sorting, and can save favourites.
**Size:** M · **Depends on:** M2 · **Requirements:** FR-LIST-05, FR-LIST-04 (saves metric), NFR-PERF-01, NFR-UX-03, NFR-UX-06, NFR-A11Y-01

**Scope in:** `search` app (selectors, filters, cache), PostGIS radius and bounding-box queries, PostgreSQL full-text search plus pg_trgm fuzzy matching, multi-select filters, sort, pagination, shareable URLs, Redis caching, read-replica routing, property card component, home page, saved properties, SEO basics, search performance test.
**Scope out:** map-based "search this area" (Post-MVP), saved searches and alerts (Post-MVP), OpenSearch (Post-MVP, only if PostgreSQL can't meet the target).

**EP-3.1 Search engine**

| ID | Story | Acceptance criteria (summary) | Req | Size |
|---|---|---|---|---|
| US-301 | As the platform, I want search-optimised indexes, so that queries stay fast at scale. | `SearchVectorField` (title A, locality B, description C) with GIN; trigram GIN on title/locality; GiST on location; partial B-tree on `(status, published_at)` and `(status, rent_amount)` where status = PUBLISHED. Vector maintained by the service on save (or a DB trigger; ADR). Indexes created with `AddIndexConcurrently`. | FR-LIST-05, NFR-PERF-01 | M |
| US-302 | As a renter, I want to search by place name with typo tolerance, so that I find homes even when I misspell a locality. | A query matches locality and title via trigram similarity (threshold tuned, default 0.3) and description via full-text. Known locality names resolve to a point or bounding box (geocoder cached). Radius selector: 2/5/10/25/50 km (default 10). Results within the radius are ranked by relevance, then distance. | FR-LIST-05 | M |
| US-303 | As a renter, I want to filter by price range, property type (multi-select) and lister tag (multi-select), so that I see only relevant homes. | Price min/max in the market currency (**Assumption**: a search is scoped to one market or currency). Type and tag multi-select are combined with OR within a filter and AND across filters. Optional bedrooms filter. Invalid parameters are ignored safely. All filters are in the URL query string. | FR-LIST-05 | M |
| US-304 | As a renter, I want to sort results, so that I can see the newest or cheapest first. | Sort: Newest (default without a query), Price low–high, Price high–low, Relevance (default with a query), Distance (when a location is set). Stable tie-breaker on `public_id`. | FR-LIST-05 | S |
| US-305 | As a renter, I want paginated results, so that pages load fast. | 20 per page. Page-number pagination capped at page 50 (beyond that: "Refine your search"). Total count shown as "1,240 homes" (exact up to 10k, then "10,000+"). | FR-LIST-05, NFR-PERF-01 | S |

**EP-3.2 Search UX**

| ID | Story | Acceptance criteria (summary) | Req | Size |
|---|---|---|---|---|
| US-306 | As a renter, I want results to update as I change filters without losing my place, so that browsing feels fluid. | HTMX `hx-get` on the filter form (300 ms debounce on text, immediate on checkbox) swaps the `#results` partial. `hx-push-url` keeps URLs shareable. Without JS, the same form submits a normal GET. Result count is announced in a polite live region. Focus is not stolen. A skeleton loader keeps the layout (no CLS). | FR-LIST-05, NFR-UX-06, NFR-A11Y-01 | M |
| US-307 | As a mobile renter, I want filters in a sheet, so that results get the full screen. | Below `lg`, a "Filters (n)" button opens a modal `<dialog>` sheet with Apply/Reset. Focus is trapped and returns on close. Above `lg`, filters show as a sidebar. | NFR-UX-06, NFR-A11Y-01 | S |
| US-308 | As a renter, I want clear property cards with an unmistakable Agent/Owner label, so that I can scan results quickly. | Card component per [UX §6](../ux/01-ux-and-page-inventory.md#6-property-card): 4:3 image with srcset and lazy loading (first row eager), price per month, title link (stretched-link pattern), locality, key facts, tag badge (icon + text + colour + border; non-colour cues), save button. Grid: 1/2/3/4 columns at <640/≥640/≥1024/≥1280 px. | NFR-UX-03, NFR-UX-06, NFR-A11Y-01 | M |
| US-309 | As a renter, I want helpful zero-result states, so that I am not stuck. | Empty state suggests widening the radius, removing filters (one-click chips) and checking spelling. "Did you mean" via trigram on locality names. | FR-LIST-05 | S |
| US-310 | As a visitor, I want a home page that gets me searching immediately, so that I find homes fast. | Search hero (location field, type, max price), recent listings, an "How credits work" explainer (10 free credits on signup, 2 credits per number), "List your property" CTA. LCP ≤ 2.5 s (p75 mobile lab). | FR-LIST-05, NFR-UX-01 | M |

**EP-3.3 Performance & caching**

| ID | Story | Acceptance criteria (summary) | Req | Size |
|---|---|---|---|---|
| US-311 | As the platform, I want hot searches cached and reads offloaded, so that latency stays low under load. | Search selectors read from the replica (DB router; configurable fallback to primary). Redis caches the list of result IDs per normalised query hash, TTL 60 s, using a global "listing version" key bumped on publish/unpublish/edit. Cards are hydrated from the DB by ID (no stale prices beyond 60 s). Cache hit ratio metric. | NFR-PERF-01, NFR-SCAL-01 | M |
| US-312 | As the tech lead, I want search performance proven, so that we meet NFR-PERF-01. | k6 on staging with the `seed_perf` dataset: standard load (default 50 req/s search, **Assumption**) p95 < 500 ms; peak (5× standard) p95 < 1000 ms; error rate < 0.1 %. EXPLAIN plans for the 6 canonical queries are stored and checked nightly for sequential scans. | NFR-PERF-01 | M |

**EP-3.4 Saved properties & SEO**

| ID | Story | Acceptance criteria (summary) | Req | Size |
|---|---|---|---|---|
| US-313 | As a renter, I want to save properties, so that I can come back to them. | Heart toggle on cards and the detail page (HTMX POST, `aria-pressed`, label "Save"/"Saved"). An anonymous click goes to login with `next` and completes the save afterwards. `SavedProperty` unique (user, property). "Saved" page `/account/saved/`. Each save and unsave increments or decrements the daily saves stat. | FR-LIST-04 (saves metric) | M |
| US-314 *(stretch)* | As the business, I want listings indexable by search engines, so that we get organic traffic. | Canonical URLs, `sitemap.xml` (published listings only), `robots.txt`, meta title/description, `noindex` on deep filter combinations and on unavailable listings. Structured data is Post-MVP. | — | S |

### Deliverables
Search page, filters, sort, pagination, caching, replica routing, card component, home page, saved properties, search perf report.

### Exit criteria and demo script
1. On a phone viewport, search for a misspelled seeded locality (e.g. "Springfeild"). Results for "Springfield" appear, with "Did you mean" shown.
2. Open Filters: select **OwnerListed** only, type = Apartment and Flat, and a price range. Apply. The count is announced (show with VoiceOver/NVDA). Sort by price low–high. Copy the URL into a new window: the same results appear.
3. Remove all matches with an extreme filter: the empty state suggests fixes.
4. Save a property while logged out: log in and confirm it is saved. Open `/account/saved/`.
5. Show the k6 report (p95 standard < 500 ms, peak < 1000 ms) and the EXPLAIN plans with no sequential scans on the 500k dataset.

---

## M4 — Credits & Contact Reveal

**Goal:** The CRITICAL monetisation path works end-to-end and holds under load. Users receive 10 promo credits once on verification, spend 2 credits to reveal a contact through an atomic, idempotent, audited debit, get an email receipt, see their balance everywhere, and can review their history.
**Size:** L · **Depends on:** M1, M2 (M0 spike informs design) · **Requirements:** FR-AUTH-04, FR-CRED-01..06, FR-PAY-05 (consumption part), FR-PROF-01, NFR-PERF-01/02, NFR-SEC-01/02, NFR-UX-01/02

**Scope in:** `credits` (CreditWallet, CreditLedgerEntry, `grant_credits`, `debit_credits`, hash chain, audit job), `leads` (ContactReveal, `reveal_contact`), promo grant and backfill, Show Number full state machine, reveal email through the outbox, transaction history (consumption and promo), header balance badge with polling and out-of-band updates, rate limiting, analytics counters, concurrency and load tests.
**Scope out:** purchases (M5); admin adjustments UI and maker-checker (M6; service stub here); the lister-pays unlock model (Post-MVP, OQ #1).

**Open Question #1 checkpoint:** before the M4 iteration starts, the PO confirms the renter-pays model. If the decision changes, re-plan EP-4.3 only. The wallet and ledger stay the same.

**EP-4.1 Wallet & ledger**

| ID | Story | Acceptance criteria (summary) | Req | Size |
|---|---|---|---|---|
| US-401 | As the business, I want each user's credits in a wallet backed by an append-only ledger, so that every credit is accounted for. | `CreditWallet` (one per user, created with the user and backfilled for existing users; `balance` integer, `CHECK (balance >= 0)`). `CreditLedgerEntry`: `public_id` (transaction ID), wallet, `entry_type` ∈ {SIGNUP_PROMO, PURCHASE, CONTACT_REVEAL, ADMIN_ADJUSTMENT, REVERSAL}, signed `amount`, `balance_before`, `balance_after`, `reference_type`/`reference_id` (e.g. property, payment order), unique `idempotency_key`, `server_process_id` (host:pid), `request_id`, `metadata` JSON, `prev_hash`, `hash`, `created_at`. DB role has no UPDATE/DELETE on the ledger table, and a trigger rejects them. | FR-CRED-03, NFR-SEC-02 | L |
| US-402 | As a developer, I want `grant_credits` and `debit_credits` services that are atomic and idempotent, so that no race can corrupt balances. | Each runs in `transaction.atomic()`. Debit uses a conditional `UPDATE wallet SET balance = balance - :n WHERE id = :id AND balance >= :n RETURNING balance` (0 rows means `InsufficientCreditsError`). The ledger row and hash are written in the same transaction while the row lock is held. A duplicate `idempotency_key` returns the original entry. No network I/O inside the transaction. Thread concurrency tests and Hypothesis invariant tests pass ([04 §7](04-testing-strategy.md#7-concurrency-tests-for-credit-debit)). | FR-CRED-02, FR-CRED-03, NFR-PERF-02, NFR-SEC-02 | L |
| US-403 | As a new user, I want 10 free credits when my account is verified, so that I can try the service immediately. | On the first login after verification (or immediately on verification if already logged in), `grant_credits(SIGNUP_PROMO, 10)` with idempotency key `promo:signup:<user_public_id>` plus a partial unique constraint (one SIGNUP_PROMO per wallet). Metadata: date, source `promo`, quantity, user ID. A one-off management command backfills users verified during M1–M3 on non-prod environments. Unverified users get nothing. **Deviation from SRS:** the grant is tied to *first verified login* rather than *first login*, because unverified accounts may not hold transactional value (GAP). | FR-AUTH-04 | M |
| US-404 | As the business, I want a nightly integrity audit, so that any discrepancy is detected within 24 h. | `audit` queue task (beat, nightly, plus on demand) per wallet: `balance == SUM(amount)` and `balance_after` of the last entry == balance; recompute and verify the SHA-256 chain. Results go to an `AuditRun` record (data-model doc). Any mismatch raises a Sentry alert and a CloudWatch alarm, and the wallet is flagged for Finance. Runtime ≤ 30 min at 1M wallets (batched, read replica). | NFR-SEC-02 | M |

**EP-4.2 Show Number & reveal**

| ID | Story | Acceptance criteria (summary) | Req | Size |
|---|---|---|---|---|
| US-405 | As a renter with enough credits, I want to click "Show Number · 2 credits" and see the lister's contact instantly, so that I can reach them. | `POST /properties/<id>/reveal/` (HTMX, CSRF, verified user). `leads.services.reveal_contact()` in one transaction: lock and debit 2 → insert `ContactReveal` (unique user+property) → enqueue the outbox email. On success the contact panel replaces the button (focus moves to the panel heading), the header balance updates out-of-band, and the toast reads **exactly** "Contact revealed. 2 credits deducted. Details emailed to you." (translatable). p95 < 500 ms. | FR-CRED-01..04, NFR-UX-02, NFR-PERF-01 | L |
| US-406 | As a renter, I want the button to behave correctly for my situation, so that I'm never charged unexpectedly. | Full state machine per [UX §7](../ux/01-ux-and-page-inventory.md#7-show-number-button-states): anonymous → "Log in to view number"; unverified → "Verify to view number"; balance 0 → Show Number hidden, "Get credits to view number" CTA; balance 1 → button visible, server rejects with the insufficient state; ≥ 2 → reveal; already revealed → contact shown free; own listing → no button; unavailable listing → hidden. The cost "2 credits" is always shown next to the action. The server re-checks every rule; the client state is advisory only. | FR-CRED-01, FR-CRED-02 | M |
| US-407 | As a renter who already paid for a contact, I want to see it again for free, so that I'm never charged twice. | A repeat POST or concurrent double-click is charged exactly once: an existing `ContactReveal` returns the contact with no debit, and a unique-constraint race rolls back the second debit. `hx-disabled-elt` prevents double submit. The contact is reachable from Transaction History and the listing page (even if later RENTED). | FR-CRED-04 | S |
| US-408 | As a renter with fewer than 2 credits, I want a clear, non-blocking message with a way to buy credits, so that I can continue. | No debit. An inline alert under the button plus a warning toast: "You need 2 credits to view this number. Your balance is 1." with a high-contrast "Buy credits" link to `/credits/buy/` (a placeholder page until M5, behind a flag). The toast does not auto-dismiss (it contains an action). | FR-CRED-06, NFR-A11Y-01 | S |
| US-409 | As the platform, I want reveal abuse limited, so that contact data can't be scraped. | Per-user limit (default 30 reveals/hour, 100/day, configurable) returns a 429 message. Velocity events are recorded for fraud rules (M6). Reveal responses send `Cache-Control: no-store`. Contact values never appear in logs, Sentry or analytics. | NFR-SEC-01, DIA-OPS-01 | S |

**EP-4.3 Reveal email (outbox)**

| ID | Story | Acceptance criteria (summary) | Req | Size |
|---|---|---|---|---|
| US-410 | As a renter, I want an email receipt with the property and contact details, so that I have a permanent record. | An `OutboxMessage` is written inside the reveal transaction, so there is no email if the debit rolls back. After commit, a Celery `email` task sends through anymail: listing link, lister name, title, full description, contact, transaction ID, credits deducted, balance after, timestamp. Retries with exponential backoff (up to 24 h). Failures alert. Tests prove a rolled-back reveal sends nothing. **Deviation from SRS:** "concurrently with the deduction" is implemented as *immediately after commit* (typically < 5 s), so we never email for a debit that didn't happen (GAP). | FR-CRED-05 | M |

**EP-4.4 Balance visibility & history**

| ID | Story | Acceptance criteria (summary) | Req | Size |
|---|---|---|---|---|
| US-411 | As a logged-in user, I want my credit balance always visible next to my profile icon and inside the dropdown, so that I always know my purchasing power. | Badge per [UX §5.2](../ux/01-ux-and-page-inventory.md#52-credit-balance-badge) on every page, including mobile. Updated out-of-band after reveal and purchase. HTMX polling every 30 s only while the tab is visible (paused when hidden; no eval/inline JS). A change is announced politely only when the user's own action caused it. Low-balance style when < 2. | FR-PROF-01, NFR-UX-01 | M |
| US-412 | As a user, I want a filterable transaction history, so that I can see every credit in and out. | `/account/transactions/`: date/time (user's timezone), type label (Promo, Purchase, Contact reveal, Adjustment, Reversal), signed amount, balance after, and a descriptive label. Consumption rows link to the property and a free "View contact". Filters: type and date range. 25 per page. Purchases show the payment method once M5 lands. Empty state. | FR-PAY-05, FR-CRED-04 | M |

**EP-4.5 Metrics & proof**

| ID | Story | Acceptance criteria (summary) | Req | Size |
|---|---|---|---|---|
| US-413 | As a lister, I want to see Show Number activity, so that I can track lead interest. | Counters in `PropertyDailyStat`: `show_number_clicks` (all attempts by logged-in users) and `reveals` (successful paid reveals). Shown on the My Properties tiles. Counters are incremented asynchronously (Redis INCR, flushed every minute by beat), so metric writes never sit on the debit path. | FR-LIST-04 | S |
| US-414 | As the tech lead, I want the credit path proven under load and contention, so that NFR-PERF-02 is demonstrated. | On staging, prod-like sizing: k6 sustains 1,000 reveal transactions/sec across distinct wallets for 10 min with p95 < 500 ms and errors < 0.1 %. Hot-wallet scenario: 200 concurrent reveals on one wallet with 20 credits gives exactly 10 successes. Post-run audit job: 0 mismatches and the chain is valid. Report stored. | NFR-PERF-02, NFR-PERF-01, NFR-SEC-02 | M |

### Deliverables
Wallet, ledger and hash chain; promo grant and backfill; reveal flow with every button state; outbox email; balance badge with polling; transaction history; audit job; load and concurrency evidence.

### Exit criteria and demo script
1. Sign up a new user and verify. On first verified login the header shows **10** and the dropdown shows 10 under the name and email. History shows "Signup bonus +10".
2. Open a listing: "Show Number · 2 credits". Click it. The contact appears, focus moves to it, the toast reads the exact SRS text, and the badge shows **8**. The email arrives in the inbox.
3. Reload the page: the contact is still shown and "No additional charge" appears. Balance is still 8.
4. Open your own listing: no Show Number button.
5. Use a seeded user with balance 1: the inline alert and toast show the "Buy credits" link, with no debit. Use a user with balance 0: the "Get credits to view number" CTA appears instead of the button.
6. Run the hot-wallet concurrency test live: exactly ⌊balance/2⌋ successes, final balance ≥ 0, audit clean.
7. Show the k6 1,000 TPS report and the nightly audit run (0 mismatches, chain verified).
8. Show the DB: an attempted `UPDATE` on the ledger as the app role fails.

---

## M5 — Payments

**Goal:** Users buy credit packages priced in their local currency through two gateways (Stripe Checkout, PayPal Orders v2). Credits are allocated within 5 s of verified payment confirmation, idempotently, with reconciliation and receipts.
**Size:** L · **Depends on:** M4 · **Requirements:** FR-PAY-01..05, FR-PROF-02, NFR-SEC-03, NFR-PERF-01, NFR-UX-06

**Scope in:** CreditPackage, CreditPackagePrice (price book per currency), currency resolution (account region, then GeoIP, then default), Purchase Credits page, `PaymentGateway` interface and adapters, PaymentOrder lifecycle, webhooks (signature-verified, stored, idempotent), success-redirect server-side verification, fulfilment through `grant_credits(PURCHASE)`, failure/retry UX, reconciliation jobs, refunds and chargebacks as REVERSAL, receipts, purchase rows in history, PCI SAQ-A evidence, prod environment rehearsal (proposed).
**Scope out:** Razorpay (stretch, only if India is a launch market); tax engine (OQ; MVP uses tax-inclusive price books); subscriptions; stored payment methods.

**EP-5.1 Packages & price books**

| ID | Story | Acceptance criteria (summary) | Req | Size |
|---|---|---|---|---|
| US-501 | As Finance, I want to manage credit packages and per-currency prices, so that pricing changes need no deployment. | `CreditPackage` (credits, active, sort, `best_value` flag). `CreditPackagePrice` (package, ISO-4217 currency, `amount_minor`, `valid_from/valid_to`). Managed in the hardened admin by Finance (audited). Seed: 20/50/120 credits (prices per OQ). Validation: per-credit price must fall as package size grows (warning). | FR-PAY-02 | M |
| US-502 | As a user, I want prices in my currency, so that I know exactly what I'll pay. | Currency resolution: account region setting, then MaxMind GeoLite2 country from IP, then market default. Only currencies present in the price book are offered; otherwise the default is used. The user can change the display currency (stored on the profile). Amounts are formatted per locale. **Deviation from SRS:** "dynamic localized currency" is an explicit price book, not live FX conversion (predictable prices and gateway settlement; GAP). | FR-PAY-02 | M |
| US-503 | As a user, I want a fast, mobile-friendly Purchase Credits page, so that buying takes seconds. | `/credits/buy/` from the dropdown and the insufficient-credit links. Package cards show credits, price, per-credit price, "Save X %" against the smallest package, and a "Best value" badge (text, not colour only). Choose a package, then a payment method (Card/Wallet via Stripe, PayPal), then redirect: ≤ 3 interactions. Current balance shown. Anonymous visitors see `/pricing/` with a login CTA. | FR-PAY-01, FR-PAY-02, NFR-UX-06 | M |

**EP-5.2 Gateway abstraction & order lifecycle**

| ID | Story | Acceptance criteria (summary) | Req | Size |
|---|---|---|---|---|
| US-504 | As a developer, I want a `PaymentGateway` interface with a registry, so that gateways are interchangeable and testable. | Interface (indicative): `create_checkout(order) -> RedirectInstruction`, `verify_payment(order) -> PaymentStatus`, `parse_webhook(request) -> GatewayEvent` (verifies the signature), `refund(...)` (optional). Registry chosen per market. Shared contract test suite ([04 §9](04-testing-strategy.md#9-contract-tests-for-adapters)). | FR-PAY-03 | M |
| US-505 | As the business, I want each purchase tracked as a PaymentOrder with a strict lifecycle, so that money and credits always reconcile. | `PaymentOrder` (`public_id`, user, package, credits snapshot, `amount_minor`, currency, gateway, `gateway_payment_id`, status — indicative: CREATED → PENDING → PAID → FULFILLED; FAILED; CANCELLED; REFUNDED/DISPUTED). Unique (gateway, `gateway_payment_id`). Price snapshot at creation. Transitions go through services and are audited. | FR-PAY-03, FR-PAY-04 | M |

**EP-5.3 Gateways**

| ID | Story | Acceptance criteria (summary) | Req | Size |
|---|---|---|---|---|
| US-506 | As a user, I want to pay by card or wallet via Stripe, so that I can buy credits securely. | Stripe Checkout Session (hosted; PCI SAQ-A) created with an idempotency key, metadata `order_public_id`, and success/cancel URLs. Webhooks: `checkout.session.completed`, `checkout.session.async_payment_succeeded`/`failed`, `charge.refunded`, `charge.dispute.created`. The signature is verified with a timestamp tolerance. The app never sees card data. | FR-PAY-03, NFR-SEC-03 | L |
| US-507 | As a user, I want to pay with PayPal, so that I can use my PayPal balance. | PayPal Orders v2: create order (intent CAPTURE), approve redirect, server-side capture on return. Webhooks `PAYMENT.CAPTURE.COMPLETED`, `PAYMENT.CAPTURE.DENIED`, `PAYMENT.CAPTURE.REFUNDED` verified via PayPal's signature-verification mechanism. | FR-PAY-03, NFR-SEC-03 | L |
| US-508 *(stretch)* | As a user in India (if it is a launch market), I want to pay with Razorpay, so that I can use local methods (UPI etc.). | Razorpay adapter passes the contract suite. Enabled per market. | FR-PAY-03 | M |

**EP-5.4 Fulfilment**

| ID | Story | Acceptance criteria (summary) | Req | Size |
|---|---|---|---|---|
| US-509 | As a buyer, I want credits in my balance within 5 s of paying, so that I can continue immediately. | `payments.services.fulfill_order(order)` is idempotent. It calls `grant_credits(PURCHASE, credits, idempotency_key="pay:<gateway>:<gateway_payment_id>")` and sets FULFILLED. It is triggered by **either** a verified webhook **or** server-side verification on the success redirect (gateway API call made *outside* the DB transaction), whichever arrives first. It never trusts client parameters. The return page shows "Confirming payment…" and polls `/payments/<id>/status/` every 2 s for up to 60 s, then shows success with the new balance and an out-of-band badge update. Allocation latency (gateway confirmation to balance updated) is measured; p95 ≤ 5 s. | FR-PAY-04, NFR-UX-01 | L |
| US-510 | As a buyer, I want a clear path when payment fails or I cancel, so that I can retry easily. | Cancel returns to `/credits/buy/` with the package preselected and an info toast. Failed or denied shows the reason category (not raw gateway text), a "Try again" option and the other gateway. Matches the flow chart "Payment successful? NO → retry". | FR-PAY-01 | S |
| US-511 | As a buyer, I want an emailed receipt and purchases in my history, so that I have proof of payment. | Receipt email through the outbox after fulfilment: order ID, package, credits, amount, currency, payment method (card brand/last 4 from the gateway, or "PayPal"), date, merchant details. History rows show the payment method. `/payments/<id>/receipt/` page (printable). | FR-PAY-05 | M |

**EP-5.5 Reconciliation, refunds, compliance**

| ID | Story | Acceptance criteria (summary) | Req | Size |
|---|---|---|---|---|
| US-512 | As Finance, I want stuck and mismatched payments detected automatically, so that no customer loses credits. | Every 5 min: orders PENDING > 10 min are re-verified with the gateway and fulfilled or failed. Daily: gateway transactions are compared with FULFILLED orders and with PURCHASE ledger entries, and mismatches alert. `PaymentWebhookEvent` stores every event (raw payload, signature status, processed_at, error) and is unique on the gateway event ID. | FR-PAY-03, NFR-SEC-02 | M |
| US-513 | As Finance, I want refunds and chargebacks reflected in credits, so that the ledger matches the money. | A refund or dispute webhook creates a REVERSAL entry for the purchased credits, up to the current balance (balance never negative). Any shortfall is recorded and the account is flagged for Finance review (M6). Refund policy per OQ. | FR-PAY-03, NFR-SEC-02 | M |
| US-514 | As the business, I want PCI DSS scope minimised and documented, so that compliance is provable. | Hosted checkout only, so no card fields on our domain. CSP allows gateway domains only where needed. SAQ-A evidence checklist in `docs/`. Webhook endpoints are CSRF-exempt but signature-verified, size-limited and rate-limited. Secrets live in Secrets Manager. | NFR-SEC-03 | S |
| US-515 *(proposed)* | As the platform team, I want the production environment provisioned without public traffic, so that M7 verifies prod instead of building it. | Prod applied from the same Terraform modules. Live gateway webhooks registered against the prod URL (no public DNS). Deploy, migration and rollback rehearsed. | NFR-SCAL-01, NFR-AVAIL-01 | M |

### Deliverables
Price books, purchase page, Stripe and PayPal adapters, webhooks, fulfilment, reconciliation, refunds/reversals, receipts, history purchase rows, PCI SAQ-A evidence, payment E2E journeys.

### Exit criteria and demo script
1. Force GeoIP to a eurozone country (test header in staging). `/credits/buy/` shows EUR prices with per-credit price and savings. Choose 50 credits, then Card.
2. Pay with a Stripe test card. Back on the site, the page shows "Confirming…" and then success. A visible timer shows the balance updated in ≤ 5 s. The receipt email arrives.
3. Repeat with a 3-D Secure test card, then a declining card: the failure page offers retry and PayPal.
4. Buy with the PayPal sandbox and confirm the history shows "PayPal".
5. Replay the same Stripe webhook from the CLI: no second credit grant.
6. Block webhook delivery and pay: the redirect verification still fulfils. Leave a PENDING order: the reconciliation job resolves it.
7. Refund from the Stripe dashboard: a REVERSAL entry appears and the audit job stays clean.

---

## M6 — Ops Console & Moderation

**Goal:** Staff can run the marketplace safely: moderation queue, tag-change review, fraud flags, finance and ledger audit, payments operations and job monitoring, all role-scoped and audited. Listers get their analytics dashboard.
**Size:** M · **Depends on:** M2 (M6a), M4 and M5 (M6b) · **Requirements:** DIA-OPS-01, FR-LIST-03, FR-LIST-04, NFR-SEC-02, NFR-AVAIL-01, NFR-A11Y-01

**Scope in:** `moderation` app (ModerationCase, fraud flags, ops views), hardened admin completion, "Report listing", tag-change review UI, fraud rules, ledger audit dashboard, admin adjustments with maker-checker, payments ops, job/outbox monitor, support user lookup with masked PII, lister analytics dashboard.
**Scope out:** KYC/Verification API (Post-MVP); automated image-similarity duplicate detection (stretch); impersonation ("login as") — **not provided**, for security reasons.

**M6a — Moderation (can start after M2)**

| ID | Story | Acceptance criteria (summary) | Req | Size |
|---|---|---|---|---|
| US-601 | As Superadmin, I want the admin fully hardened, so that the most powerful interface is the best protected. | Only reachable at `/ops/admin/`. Staff MFA (from M1). Idle timeout 30 min for staff. Optional WAF IP allowlist. Financial models (ledger, orders, webhook events) read-only in admin, with no delete permission. Every admin change written to AuditLog (actor, object, diff). Superadmin count ≤ 2. | DIA-OPS-01, NFR-SEC-02 | M |
| US-602 | As staff, I want an ops console home with work queues, so that I see what needs attention. | `/ops/`: counts for the moderation queue, pending tag changes, open fraud flags, audit mismatches, stuck payments, outbox backlog and failed tasks. Each tile links to its queue. Visible tiles depend on the user's group. Same design system and a11y standards as the public site. | DIA-OPS-01 | M |
| US-603 | As a renter, I want to report a suspicious listing, so that the marketplace stays trustworthy. | "Report listing" link on the detail page opens a `<dialog>` with reason (fake, wrong tag, already rented, offensive, scam, other) and details. Rate-limited. Creates or attaches to a `ModerationCase`. Confirmation toast. | DIA-OPS-01 | S |
| US-604 | As a Moderator, I want a moderation queue with actions, so that I can resolve reports consistently. | `/ops/moderation/`: filter by reason, age, status; case detail with listing snapshot, reports and history. Actions: dismiss, request changes (email to lister), suspend listing (hidden from search; reveals blocked), restore, ban user (Superadmin only). Reason code required. Lister notified. Every action audited. | DIA-OPS-01, FR-LIST-04 | L |
| US-605 | As a Moderator, I want a proper tag-change review screen, so that decisions are evidence-based. | `/ops/tag-changes/`: queue sorted by age, with SLA indicator. Detail shows current vs requested tag, reason, evidence (signed URL from the private bucket, 5-minute expiry), and lister history. Approve or reject with a reason. Tag updated atomically with an AuditLog entry and email. Replaces the M2 admin action. | FR-LIST-03 | M |

**M6b — Finance, fraud, analytics (after M4/M5)**

| ID | Story | Acceptance criteria (summary) | Req | Size |
|---|---|---|---|---|
| US-606 | As a Fraud reviewer (Moderator or Support), I want automatic fraud flags, so that abuse is caught early. | Rules (configurable thresholds): reveal velocity per user; many accounts sharing a device fingerprint, IP or phone prefix within 24 h; promo-only accounts with immediate reveals; chargebacks/disputes; listings with duplicate contact across many accounts. Each creates a flag with evidence. Actions: dismiss, freeze wallet (debits blocked; balance kept), escalate to a moderation case. | DIA-OPS-01, FR-AUTH-04 (abuse) | L |
| US-607 | As Finance, I want a ledger audit dashboard, so that I can prove credit integrity. | `/ops/finance/ledger-audit/`: last runs, wallets checked, mismatches, chain-verification status, and a "re-run for wallet" action. Wallet view shows the ledger (read-only, paginated) with hash status. Export CSV (Finance only, audited). | NFR-SEC-02 | M |
| US-608 | As Finance, I want admin credit adjustments with four-eyes approval, so that manual changes are controlled. | Create an ADMIN_ADJUSTMENT request (amount ±, mandatory reason, ticket reference). A *different* Finance user approves. Then `grant_credits`/`debit_credits` run with `entry_type=ADMIN_ADJUSTMENT`. The user is notified (configurable). Fully audited. | NFR-SEC-02 | M |
| US-609 | As Finance or Support, I want payments operations tools, so that I can resolve customer payment issues. | `/ops/finance/payments/`: search by order ID, user, gateway ID; order timeline (events, webhooks, ledger entries); "Re-verify with gateway" action (idempotent fulfil). Webhook event log with failures. | FR-PAY-03, FR-PAY-04 | M |
| US-610 | As Support, I want to look up a user safely, so that I can help without exposing data. | `/ops/users/`: search by email (blind-index exact match) or public ID. Profile shows PII masked by default. "Reveal" requires a reason and is audited. Actions: resend verification, revoke sessions, view wallet summary (read-only). | NFR-SEC-01, DIA-OPS-01 | M |
| US-611 | As the platform team, I want job and outbox monitoring in the console, so that background failures are visible. | `/ops/jobs/`: queue depths per Celery queue, oldest message age, outbox pending/failed counts with retry action, last beat run per schedule, failed tasks in the last 24 h. Backed by CloudWatch metrics and alarms. No Flower exposed publicly. | DIA-OPS-01, NFR-AVAIL-01 | M |
| US-612 | As a lister, I want an analytics dashboard per listing, so that I can track ROI and engagement. | `/my-properties/<id>/analytics/` and the dashboard summary: views, saves, Show Number clicks and reveals for 7/30/90 days. Chart plus an accessible data table (each chart has a table equivalent). Near-real-time via HTMX polling every 60 s while visible ("Updated 12 s ago"). Counts lag ≤ 1 min. **Assumption:** "real-time" in the SRS means ≤ 1 minute freshness (GAP). | FR-LIST-04, FR-PROF-02 | M |

### Deliverables
Ops console, moderation, tag-change review, fraud flags, finance audit and adjustments, payments ops, job monitor, support lookup, lister analytics; role × view authorisation matrix tests.

### Exit criteria and demo script
1. As a renter, report a listing ("wrong tag"). As Moderator, open `/ops/`: the queue count is 1. Suspend the listing: it disappears from search and Show Number is hidden. The lister gets an email. AuditLog shows the action.
2. As a lister, request a tag change with evidence. As Moderator, view the evidence (signed URL) and approve. The card badge changes. AuditLog entry exists.
3. Run the fraud-scenario script (20 rapid reveals): a flag appears. Freeze the wallet: the next reveal is blocked with a support message.
4. As Finance A, request a +10 adjustment. Finance A cannot approve it; Finance B approves. The ledger entry and email follow.
5. Show the ledger audit dashboard (clean) and `/ops/jobs/` (queues healthy).
6. As a lister, open analytics: tiles and table update within 1 min of a new view or reveal.

---

## M7 — Hardening & Launch Readiness

> **Hosting change (2026-10-27):** M7 now also covers choosing and provisioning the hosting target (OQ-50 to OQ-54), the CI deploy job, rewriting the runbooks and alerts for that target (register H-08), PITR for the database, and the concurrency re-run on its managed Postgres. See [architecture/05 §10](../architecture/05-hosting-and-deployment.md#10-deferred-work-when-a-target-is-chosen).

**Goal:** Verify (not build for the first time) performance, security, accessibility, privacy and recoverability on production, then go live with a rollback plan and hypercare.
**Size:** L · **Depends on:** M0–M6 · **Requirements:** NFR-PERF-01/02, NFR-AVAIL-01, NFR-SEC-01/02/03, NFR-SCAL-01, NFR-MAINT-01, NFR-A11Y-01

| ID | Story | Acceptance criteria (summary) | Req | Size |
|---|---|---|---|---|
| US-701 | As the platform team, I want production infrastructure finalised, so that it is resilient and secure. | RDS Multi-AZ with read replica and PITR (retention ≥ 7 days, **Assumption** 14), ECS autoscaling (CPU/requests and queue depth), WAF managed plus rate rules, KMS CMKs, CloudFront, budgets and cost alarms, least-privilege IAM. `terraform plan` clean. Config drift detection. | NFR-SCAL-01, NFR-AVAIL-01 | M |
| US-702 | As the tech lead, I want final load, soak and spike tests on prod-like infrastructure, so that NFRs are proven. | Search: standard p95 < 500 ms, peak p95 < 1000 ms. Reveal: 1,000 TPS for 15 min, p95 < 500 ms. Purchase webhook burst of 100/s. 4 h soak at 50 % peak with no memory growth > 10 %. Spike 0 → peak in 60 s. Post-test audit clean. Capacity plan written. | NFR-PERF-01, NFR-PERF-02 | L |
| US-703 | As the security owner, I want independent security verification, so that launch risk is acceptable. | External pen test (scope: web, auth, credits, payments, ops). All Critical/High fixed and re-tested, Medium triaged. ZAP full scan clean of High. OWASP ASVS L2 checklist completed. Dependencies and images have no unresolved Critical/High. Secrets rotation drill. Threat model updated. | NFR-SEC-01..03 | L |
| US-704 | As a user relying on assistive technology, I want the product audited for WCAG 2.1 AA, so that I can use every feature. | Manual audit of all pages in the [page inventory](../ux/01-ux-and-page-inventory.md#4-page-inventory) using the [04 §11](04-testing-strategy.md#11-accessibility-tests) checklist (NVDA+Firefox, VoiceOver macOS/iOS, TalkBack, keyboard only, 200 %/400 % zoom). All A/AA failures fixed. Accessibility statement published. | NFR-A11Y-01 | L |
| US-705 | As the DPO/security owner, I want PII protection verified, so that a DB or log leak exposes nothing useful. | A DB snapshot inspection shows ciphertext for contact phone/email and other designated PII. Blind indexes work. Logs and Sentry sampled show no PII. Field-key rotation rehearsed. S3 private bucket blocks public access. Data map and retention schedule documented. | NFR-SEC-01 | M |
| US-706 | As the operator, I want backups proven restorable, so that NFR-AVAIL-01 is met. | PITR restore to a new instance. App smoke tests and the ledger audit pass on the restored DB. Measured RPO ≤ 5 min and RTO ≤ 1 h (proposed targets, OQ). Drill report. Quarterly drill scheduled. | NFR-AVAIL-01 | M |
| US-707 | As on-call staff, I want runbooks, so that common incidents are handled consistently. | Runbooks: payment API failure (per gateway), webhook backlog, DB performance degradation, Redis outage, email/SMS provider outage, ledger audit mismatch, Celery backlog, suspected credential stuffing, deploy rollback, restore from backup. Each has detection, impact, steps and verification. Tested in a game day. | NFR-AVAIL-01 | M |
| US-708 | As the operator, I want SLOs, dashboards and alerts, so that we detect issues before users do. | SLOs: availability 99.9 %/month (proposed), search and reveal p95 latency, allocation ≤ 5 s p95, email send ≤ 60 s p95. Dashboards. Alerts routed to on-call. Synthetic checks (home, search, login, reveal on a canary account in prod). | NFR-AVAIL-01, NFR-PERF-01 | M |
| US-709 | As the business, I want legal and policy pages, so that we launch compliantly. | Terms, Privacy, Cookies (consent banner if required by market), Credits & Refund policy, Accessibility statement, Contact/Help. Content supplied by the client (OQ). | — | S |
| US-710 | As the operator, I want launch data and accounts prepared, so that day one works. | Packages and price books entered and verified by Finance. Staff accounts with MFA. Groups verified. Email domain authenticated (SPF/DKIM/DMARC pass). Live gateway keys and webhooks verified with a real low-value transaction (then refunded). | FR-PAY-02, FR-PAY-03 | S |
| US-711 | As the team, I want a controlled go-live with hypercare, so that issues are fixed fast. | Go/No-Go meeting using [05 §7](05-definition-of-done-and-workflow.md#7-release-checklist). DNS cutover. Smoke tests. Rollback plan rehearsed. Two-week hypercare with daily triage. Post-launch review. | NFR-AVAIL-01 | M |
| US-712 | As the business, I want real-user Core Web Vitals verified, so that the mobile experience is good. | Lab: Lighthouse CI budgets pass on key pages. Field: RUM beacons show LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1 at p75 on mobile within 2 weeks of launch. | NFR-UX-06, NFR-PERF-01 | S |

### Exit criteria (Go/No-Go)
All M7 stories Done. Zero open S1/S2 defects. Pen-test Critical/High closed. Accessibility audit AA pass. Load test report meets NFRs. Restore drill within RPO/RTO. Runbooks reviewed. On-call rota in place. Stakeholder sign-off recorded.

**Demo:** walk through the Go/No-Go evidence pack, then run a live production smoke test (signup, verify, promo, search, reveal, purchase of the smallest package then refunded) on a staff test account.

---

## Post-MVP Backlog

Prioritised by the PO after launch. Items marked ⚑ may move into MVP depending on open questions.

| ID | Item | Notes / dependency | Req |
|---|---|---|---|
| US-901 | Social sign-on (Google, Apple), if not done as US-119 | Apple Developer account | FR-AUTH-02 |
| US-902 | User MFA (TOTP, passkeys/WebAuthn) for renters and listers | allauth MFA already enabled for staff | NFR-SEC-01 |
| US-903 | KYC / Verification API: owner identity, ownership proofs, "Verified owner" badge | `verification` app; private bucket and hooks exist since M2 | DIA-KYC-01 |
| US-904 | Lister-pays "lead unlock" model (flow-chart variant) | OQ #1. New ledger reason code. `leads` app extension. Feature flag. | DIA-LEAD-01 |
| US-905 ⚑ | Free inquiry / lead form and lister notification of new leads | Messaging, anti-spam, notifications | DIA-LEAD-01 |
| US-906 | Saved searches and new-listing alerts (email) | `notifications` | FR-LIST-05 |
| US-907 | Map-based search ("search this area", clustering) | Map provider costs | FR-LIST-05 |
| US-908 | OpenSearch for search, only if PostgreSQL misses targets at scale | ADR with evidence | NFR-PERF-01 |
| US-909 | Versioned JSON API (DRF) plus SimpleJWT for mobile apps | `/api/v1/` | — |
| US-910 | Additional languages and RTL locales | i18n-ready from M0 | NFR-UX-06 |
| US-911 ⚑ | Account closure and personal-data export (GDPR/DPDP rights) | Depends on launch markets (OQ) | NFR-SEC-01 |
| US-912 ⚑ | Tax engine (VAT/GST on digital goods), tax invoices | OQ before M5 | FR-PAY-02 |
| US-913 | Razorpay (if not done as US-508) and further local gateways | Market-driven | FR-PAY-03 |
| US-914 | Dark mode | Tokens structured for it | NFR-UX-06 |
| US-915 | Duplicate-image and listing detection (perceptual hash) | Moderation | DIA-OPS-01 |
| US-916 | Referral credits programme | New ledger reason code | — |

---

## Requirement → milestone traceability (summary)

| Requirement | Milestone(s) | Stories |
|---|---|---|
| FR-AUTH-01/03/05 | M1 | US-101–US-109 |
| FR-AUTH-02 | M1 stretch / Post-MVP | US-119 / US-901 |
| FR-AUTH-04 | M4 | US-403 (abuse: US-105, US-606) |
| FR-AUTH-06 | M1 | US-104, US-113, US-114 |
| FR-LIST-01/02/03 | M2 | US-201–US-214 |
| FR-LIST-04 | M2, M3, M4, M6 | US-215–US-218, US-313, US-413, US-612 |
| FR-LIST-05 | M3 | US-301–US-312 |
| FR-CRED-01..06 | M4 | US-405–US-410 |
| FR-PAY-01..04 | M5 | US-501–US-514 |
| FR-PAY-05 | M4 (consumption), M5 (purchases) | US-412, US-511 |
| FR-PROF-01..03 | M1, M4 | US-107, US-110–US-112, US-116, US-411 |
| NFR-PERF-01/02 | M0 spike, M3, M4, M7 | US-012, US-312, US-414, US-702 |
| NFR-AVAIL-01 | M0, M6, M7 | US-006, US-611, US-706–US-708 |
| NFR-SEC-01..03 | M0–M7 (cross-cutting), M7 verification | US-015, US-114, US-208, US-514, US-703, US-705 |
| NFR-SCAL-01 | M0, M1, M5, M7 | US-011, US-118, US-515, US-701 |
| NFR-MAINT-01 | M0 (gates), every story (DoD) | US-002, US-010, US-013 |
| NFR-UX-01..06 | M0–M5 | US-008, US-116, US-204, US-308, US-411, US-503 |
| NFR-A11Y-01 | Every story (DoD) + M7 audit | US-008, US-704 |
| DIA-OPS-01 | M1 (MFA), M2 (minimal), M6 | US-114, US-214, US-601–US-611 |
| DIA-KYC-01, DIA-LEAD-01 | Post-MVP | US-903–US-905 |
