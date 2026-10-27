# ADR-0003: Server-side sessions instead of JWT

Decides how browser users stay authenticated and how credentials are stored: Django server-side sessions (Valkey-cached, PostgreSQL-backed) with hardened cookies, django-allauth for the flows, and Argon2id password hashing. JWT is reserved for a future mobile/public API.

Status: Draft v0.1 (2026-10-21)

| | |
|---|---|
| Decision status | Proposed |
| Date | 2026-10-21 |
| Deciders | Tech Lead (owner); Security; PO acknowledges the SRS deviation |
| Consulted | QA, Platform |
| Supersedes / superseded by | — |
| Requirements | SRS §3.1–3.4 (sign-up, verification, login, hashing "e.g. bcrypt", "encryption protocols (e.g., JWT for session management)", forgot password), §7.3 (logout terminates server session, invalidates all tokens, clears local artefacts), §9.1; FR-AUTH-05, NFR-SEC-01 |
| Gap / open question | GAP-07 (known issue #7); OQ-SEC-01 (Argon2 parameters) |
| Related | [Security §6.2](../quality/01-security-and-compliance.md#62-authentication-and-sessions) · [02 T11–T12](../architecture/02-tech-stack.md#2-technology-choices-by-layer) · [01 §12 caching (sessions)](../architecture/01-system-architecture.md#12-caching-strategy) · [ADR-0002](0002-server-rendered-htmx-alpine-tailwind.md) |

## Context and problem statement

SRS §3.4 asks for "industry-standard hashing (e.g., bcrypt) and encryption protocols (e.g., JWT for session management)". SRS §7.3 asks that logout "securely terminate the user's session on the server side, invalidate all active session tokens, and clear any associated local authentication artifacts".

These two statements pull in different directions. A JWT is a self-contained, signed token: the server does not store it, so it stays valid until it expires. "Invalidating" it requires a server-side denylist, which turns the JWT back into a server-side session with extra complexity. The UI is server-rendered ([ADR-0002](0002-server-rendered-htmx-alpine-tailwind.md)); there is no JavaScript client that needs a bearer token in the MVP.

**Question:** what session mechanism best meets the SRS intent (secure login, real server-side logout, revocable sessions) for a server-rendered Django application?

## Decision drivers

1. **Real revocation:** logout, "log out other devices", password change and staff actions must end sessions immediately (SRS §7.3).
2. **Resistance to token theft:** no credentials readable by JavaScript (XSS impact).
3. **CSRF protection** on every state-changing request, including HTMX.
4. **Fit with the framework:** allauth (verification, reset, MFA, user sessions) and the Django admin use Django sessions natively.
5. **Performance:** session lookup must not threaten the p95 targets (SRS §8.1).
6. **Future mobile API** without redesign.

## Considered options

1. **Django server-side sessions** (`cached_db`: Valkey cache + PostgreSQL), `__Host-` cookies, allauth.
2. **JWT access + refresh tokens in HttpOnly cookies**, with a server-side denylist for logout.
3. **JWT in `localStorage`**, sent as a bearer header.
4. **External identity provider** (Amazon Cognito, Auth0) with OIDC, plus a local Django session.

## Decision outcome

**Chosen option 1: Django server-side sessions**, because deleting a server-side session is a true, immediate revocation, which is exactly what SRS §7.3 asks for. The cookie is an opaque random identifier, not a credential that can be replayed after logout.

Decision details (full control list in [security §6.2](../quality/01-security-and-compliance.md#62-authentication-and-sessions)):

| Topic | Setting |
|---|---|
| Session engine | `django.contrib.sessions.backends.cached_db`, cache alias `sessions` on the Valkey cache cluster; JSON serializer. Losing the cache never logs users out (falls back to PostgreSQL) |
| Cookies | `SESSION_COOKIE_NAME="__Host-sessionid"`, `CSRF_COOKIE_NAME="__Host-csrftoken"`; `Secure`, `HttpOnly`, `SameSite=Lax`, no `Domain` attribute |
| Lifetime | Members: browser session, or 14 days with "remember me". Staff: 30-minute idle, 12-hour absolute. Re-authentication within 10 minutes for sensitive actions |
| Rotation | Session key cycled on login, privilege change and password change |
| Logout | POST only; `session.flush()`; response header `Clear-Site-Data: "cache", "cookies", "storage"` (clears local artefacts, SRS §7.3); `Cache-Control: no-store` on authenticated pages |
| All devices | `allauth.usersessions` lists sessions and ends the others; password change or reset ends all other sessions |
| Flows | django-allauth: email login, mandatory verification (email link or phone OTP via Twilio Verify), password reset with time-limited links, MFA (mandatory for staff), optional Google/Apple |
| Password hashing | `PASSWORD_HASHERS = [tuned Argon2id subclass, BCryptSHA256PasswordHasher, PBKDF2PasswordHasher]`. Argon2id is the default; bcrypt is retained as a fallback hasher, and older hashes upgrade on login. Argon2 parameters are chosen by benchmark on the production task size (100–250 ms per hash, < 64 MiB) and recorded in a follow-up ADR (OQ-SEC-01) |
| Future API | Post-MVP DRF API under `/api/v1/` uses SimpleJWT: short-lived access tokens, rotating refresh tokens with a blacklist, calling the same services. Browser sessions are not affected |

### Consequences

- **Positive:**
  - Logout and "log out other devices" are immediate and complete: there is nothing left to replay.
  - No authentication material is readable by JavaScript; XSS cannot steal a session token (HttpOnly), and the strict CSP limits XSS in the first place.
  - Built-in CSRF protection works unchanged with HTMX (`X-CSRFToken` header).
  - allauth and the admin work out of the box, which saves weeks of security-sensitive code.
- **Negative:**
  - Every authenticated request reads the session (one Valkey `GET`, rarely a database fallback). *Mitigation:* sub-millisecond in-VPC cache reads; measured in the M4 load test.
  - Sessions are state in Valkey/PostgreSQL. *Mitigation:* `cached_db` makes the cache disposable; the web tier remains stateless ([04 §1 P6](../architecture/04-infrastructure-and-deployment.md#1-principles)).
  - Cookies are bound to the web origin, so a mobile app cannot reuse them. *Mitigation:* JWT for the post-MVP API, as above.
- **Neutral:** Argon2id costs more CPU and memory per login than PBKDF2; the login latency budget (p95 ≤ 800 ms) and login rate limits account for it ([NFR §5.3](../quality/02-nfr-performance-and-scalability.md#53-argon2-capacity)).

### Confirmation

- `manage.py check --deploy --fail-level WARNING` passes with production settings in CI.
- Tests: logout deletes the server session and sets `Clear-Site-Data`; a replayed old session cookie after logout is rejected; password change ends other sessions; staff idle timeout enforced.
- A settings test asserts Argon2 is first and bcrypt is present in `PASSWORD_HASHERS` ([testing §4](../delivery/04-testing-strategy.md#4-test-settings-and-environments)).
- ZAP scans report no cookie-flag findings.

## Pros and cons of the options

### 1. Server-side sessions (chosen)

- Good, because revocation is immediate and complete.
- Good, because the cookie carries no claims to leak or tamper with.
- Good, because it is native to Django, allauth and the admin.
- Bad, because a session read is needed per request (cheap, cached).

### 2. JWT in HttpOnly cookies with a denylist

- Good, because the same token format could later serve a mobile API.
- Bad, because real logout needs a denylist checked on every request, which is a server-side session in disguise, with more moving parts (refresh rotation, clock skew, key rotation).
- Bad, because allauth and the admin still need Django sessions, so the system would run two mechanisms.

### 3. JWT in `localStorage`

- Bad, because any XSS can exfiltrate the token, and logout cannot invalidate a stolen copy. Rejected outright.

### 4. External identity provider

- Good, because MFA, social login and account security features are outsourced.
- Bad, because of cost per monthly active user, UX constraints on the sign-up flow (real-time validation, SRS §3.1), and data-residency questions; the app would still need a local session and user model.

## Deviations from the SRS

**Deviation from SRS §3.4:** the SRS names "JWT for session management" as an example. We use server-side sessions for browsers because they satisfy SRS §7.3 ("invalidate all active session tokens") fully, whereas stateless JWTs cannot be invalidated without rebuilding server-side state. JWT remains the plan for the post-MVP API. Recorded as GAP-07 and DEV-SEC-1.

**Not a deviation:** SRS §3.4 says "industry-standard hashing (e.g., bcrypt)". Argon2id is Django's recommended hasher and OWASP's first choice; bcrypt is kept as a fallback hasher, so the SRS example is still supported (DEV-SEC-2).

## Follow-ups

| # | Action | Owner | Milestone |
|---|---|---|---|
| 1 | Benchmark Argon2 parameters on the production task size; record them in a follow-up ADR | Tech Lead | M1 (OQ-SEC-01) |
| 2 | Logout, session and cookie tests | QA | M1 (US-107, US-108) |
| 3 | Design the DRF + SimpleJWT API when a mobile client is scheduled | Tech Lead | Post-MVP |

## More information

- Revisit if a first-party mobile app or third-party API consumers are scheduled (additive), or if a corporate SSO requirement for staff appears (an IdP for staff only is compatible with this decision).
