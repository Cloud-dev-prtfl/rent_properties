# Requirements Catalog

Purpose: every requirement in the SRS (and the few that only the HLRD or the diagrams add), rewritten as atomic, testable statements with stable IDs, MoSCoW priority, acceptance criteria and target milestone. This is the single list that stories, tests and design documents trace to.

Status: Draft v0.1 (2026-10-21)

Related: [01 Source Documents](01-source-documents.md) · [03 Gap Analysis & Decisions](03-gap-analysis-and-decisions.md) · [04 Open Questions](04-open-questions.md) · [05 Glossary](05-glossary.md) · [Milestones & Backlog](../delivery/02-milestones-and-backlog.md)

---

## 0. How to read this catalog

### 0.1 ID scheme

`<FAMILY>-<AREA>-<GG>.<n>`

- **`<FAMILY>-<AREA>-<GG>` is the requirement group.** For SRS-sourced groups it maps 1:1 to an SRS subsection (or a clearly separable part of one). Group IDs are exactly the ones already used in the delivery backlog ([02 §0.1](../delivery/02-milestones-and-backlog.md#01-requirement-reference-key)), so a story that cites `FR-LIST-04` cites the whole group.
- **`.<n>` is one atomic, testable requirement** inside the group. Tests and acceptance records cite atomic IDs (`FR-LIST-04.3`).
- IDs are **stable**: a removed requirement keeps its ID with status *Withdrawn*; new ones get the next free number. IDs are never reused.

| Family | Area | Scope |
|---|---|---|
| FR-AUTH | Authentication, verification, promo credits, RBAC | SRS §3 (+ HLRD §3 RBAC) |
| FR-LIST | Listing submission, fields, tag, management, search | SRS §4 |
| FR-CRED | Credit consumption: Show Number, check, debit, display, email, insufficient credit; wallet foundation | SRS §5 (+ derived) |
| FR-PAY | Purchase access, packages, gateways, allocation, history; refunds/reconciliation | SRS §6 (+ derived) |
| FR-PROF | Profile icon, dropdown, tabs, logout | SRS §7 |
| FR-SAVE | Saved properties | Derived (GAP-19) |
| FR-OPS | Ops console: admin hardening, moderation, tag review, fraud, finance, support, jobs | Derived (diagram, GAP-18) |
| FR-NOTIF | Transactional notification infrastructure | Derived (SRS §5.5 "monitored service", diagram) |
| FR-LEAD, FR-KYC | Inquiry leads / lister-pays unlock; owner verification | Derived, **Post-MVP** |
| NFR-PERF | Latency, concurrency | SRS §8.1, §8.2 |
| NFR-AVAIL | Backups, restore testing, runbooks, SLA/RPO/RTO | SRS §8.3 (+ proposed targets) |
| NFR-SEC | Encryption/PII, credit integrity, PCI; app-security and privacy baselines | SRS §9 (+ derived) |
| NFR-SCAL | Cloud native, horizontal scale, IaC | SRS §10.1 |
| NFR-CODE | Code standards, review, coverage | SRS §10.2 |
| NFR-OBS | Observability | Derived |
| NFR-UX | Transparency, navigation, guided listing, mobile-first; i18n readiness | SRS §11 (+ derived) |
| NFR-A11Y | WCAG 2.1 AA | SRS §12 |

### 0.2 Column meanings

| Column | Meaning |
|---|---|
| **Src** | `SRS` = stated in SRS (section in the group heading). `HLRD` = only in the HLRD. `Derived (GAP-nn / DIA)` = not in the SRS; added because a gap decision, diagram or another requirement needs it. Derived items are always labelled. |
| **Pri** | MoSCoW. SRS "CRITICAL" and "MUST/must/shall" = **Must**. "should" = **Should**. "(optional)" = **Could**. Explicitly excluded = **Won't** (kept for traceability). |
| **MS** | Target milestone M0–M7 or Post-MVP ([milestones](../delivery/02-milestones-and-backlog.md)). "M2→M6" means first delivered in M2, completed in M6. |
| **Acceptance criteria** | Bullet checks, automated wherever possible. CRITICAL groups also have Given/When/Then scenarios. |

**Deviation from SRS** and **Assumption** markers point to the gap entry in [03](03-gap-analysis-and-decisions.md) that justifies them. Unknowns are listed in [04](04-open-questions.md).

### 0.3 Cross-reference aliases

Other documents use some alternative IDs. They resolve as follows:

| Reference used elsewhere | Where | Catalog ID(s) |
|---|---|---|
| Group IDs `FR-AUTH-01`…`NFR-A11Y-01` | [Backlog §0.1](../delivery/02-milestones-and-backlog.md#01-requirement-reference-key) | Identical (they are the group IDs here) |
| `NFR-MAINT-01` | Backlog | `NFR-CODE-01` |
| `DIA-OPS-01` | Backlog | `FR-OPS-01` … `FR-OPS-07` |
| `DIA-KYC-01` | Backlog | `FR-KYC-01` |
| `DIA-LEAD-01` | Backlog | `FR-LEAD-01` |
| `FR-LIST-19`, `FR-LIST-20` | [01 §6 F-03](01-source-documents.md#6-fidelity-assessment-of-the-diagrams) | `FR-LIST-04.3` (mark rented), `FR-LIST-04.4` (unlist) |
| `FR-OPS-*` | [01 §7](01-source-documents.md#7-mapping-diagram-elements-to-canonical-design-names) | `FR-OPS-01` … `FR-OPS-07` |
| `OQ-LST-nn`, `A-n` | Listings design §15, Architecture §18 | Consolidated in [04](04-open-questions.md) §4 |

---

## 1. Summary

| Family | Groups | Atomic requirements | Must | Should | Could | Won't / Post-MVP |
|---|---|---|---|---|---|---|
| FR-AUTH | 6 | 33 | 27 | 3 | 3 | 0 |
| FR-LIST | 5 | 50 | 44 | 6 | 0 | 0 |
| FR-CRED | 8 | 38 | 35 | 3 | 0 | 0 |
| FR-PAY | 6 | 35 | 28 | 6 | 0 | 1 |
| FR-PROF | 3 | 21 | 19 | 2 | 0 | 0 |
| FR-SAVE / FR-OPS / FR-NOTIF | 9 | 25 | 17 | 8 | 0 | 0 |
| FR-LEAD / FR-KYC | 2 | 7 | 1 | 0 | 0 | 6 |
| NFR (all) | 21 | 88 | 77 | 11 | 0 | 0 |
| **Total** | **60** | **297** | **248** | **39** | **3** | **7** |

Counts are by the **Pri** column. Post-MVP items are counted under Won't (for MVP) even when their eventual priority is higher.

---

## 2. Authentication & accounts (FR-AUTH)

SRS §3.0 preamble: "The system implements a rigid authorization for users." HLRD: "rigid Role-Based Access Control (RBAC) model … for three core user types."

### FR-AUTH-01 — Sign-up (SRS §3.1)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| FR-AUTH-01.1 | A visitor can register with email and password. | SRS | Must | M1 | • Fields: name, email, password, Terms/Privacy acceptance (versioned).<br>• Success creates one `accounts.User` in state *unverified* and starts verification (FR-AUTH-03).<br>• A double submit creates exactly one account. |
| FR-AUTH-01.2 | Email format is validated in real time (on blur / debounced input) and again on the server. | SRS | Must | M1 | • Invalid format shows an inline error within 500 ms of blur, before submit.<br>• Server rejects invalid format even with JS disabled. |
| FR-AUTH-01.3 | Password strength, including complexity rules, is validated in real time with visible feedback, and enforced on the server. | SRS | Must | M1 | • Strength meter and rule checklist update as the user types.<br>• Server enforces: min 12 characters, not in common-password list, not similar to name/email, not all numeric (**Assumption**, GAP-27, OQ-15).<br>• Rejected passwords never reach logs. |
| FR-AUTH-01.4 | Email uniqueness is validated in real time (case-insensitive, normalised). | SRS | Must | M1 | • `John@X.com` and `john@x.com` are the same account.<br>• Taken email shows "An account with this email already exists. Log in or reset your password."<br>• Check endpoint is rate-limited per IP; DB unique constraint is the final guard (GAP-28). |
| FR-AUTH-01.5 | Sign-up abuse controls protect promo credits. | Derived (GAP-06) | Must | M1 | • Disposable-email domains rejected (updatable blocklist).<br>• Per-IP sign-up rate limit; CAPTCHA can be switched on by feature flag.<br>• Blocked attempts written to `core.AuditLog`. |

### FR-AUTH-02 — Social sign-on (SRS §3.1, "(optional)")

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| FR-AUTH-02.1 | A visitor can sign up / log in with Google. | SRS | Could | M1 stretch, else Post-MVP | • allauth Google provider; account created or linked on first use. |
| FR-AUTH-02.2 | A visitor can sign up / log in with Apple. | SRS | Could | M1 stretch, else Post-MVP | • allauth Apple provider; works with "Hide my email" relay addresses. |
| FR-AUTH-02.3 | Social accounts link to an existing account only through a verified email, and count as verified only if the provider asserts a verified email. | Derived (GAP-24) | Could | Same as above | • No account takeover by registering an unverified email at the provider.<br>• Promo grant rules (FR-AUTH-04) apply unchanged. |

### FR-AUTH-03 — Account verification (SRS §3.2)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| FR-AUTH-03.1 | New accounts start in state *unverified*. | SRS | Must | M1 | • `is_verified` (or equivalent) false until FR-AUTH-03.2 or 03.3 succeeds. |
| FR-AUTH-03.2 | The account is activated by email confirmation (single-use, time-limited code or link). | SRS | Must | M1 | • Link/code expires after 24 h (**Assumption**) and works once.<br>• Resend has a 60 s cooldown. |
| FR-AUTH-03.3 | The account can alternatively be activated by phone OTP. | SRS | Should | M1 | • Twilio Verify: 6-digit code, 10 min expiry, max 5 attempts, resend cooldown 60 s, rate limits per phone and IP.<br>• Phone normalised to E.164; unique among verified accounts (blind index).<br>• Either method activates the account (**Assumption**, GAP-26, OQ-10). |
| FR-AUTH-03.4 | Unverified accounts are blocked from transactional activities: creating/publishing listings, Show Number (consuming credits), purchasing credits, saving properties. | SRS | Must | M1 | • Every protected URL and service returns a "Verify your account" page/fragment with a CTA; matrix test covers all of them.<br>• Enforced in services (`can_transact(user)`), not only views.<br>• Browsing, search and profile editing remain available. |
| FR-AUTH-03.5 | Unverified accounts receive no promotional credits. | SRS | Must | M1→M4 | • No `SIGNUP_PROMO` ledger entry exists for an unverified user (see FR-AUTH-04.1). |
| FR-AUTH-03.6 | Verification events are audited. | Derived | Should | M1 | • `AuditLog` row on verification success (method, timestamp); no OTP or token values stored. |

### FR-AUTH-04 — Initial credit allocation (SRS §3.3, CRITICAL)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| FR-AUTH-04.1 | On the first successful login after the account becomes verified, the system automatically grants **10** complimentary credits. If the user verifies while already logged in, the grant happens at verification. | SRS | Must | M4 | • Balance goes from 0 to 10 with no user action.<br>• **Deviation from SRS:** "first login after registration" becomes "first verified login" (GAP-06). |
| FR-AUTH-04.2 | The grant is one-time per user and idempotent. | SRS | Must | M4 | • DB partial unique constraint: at most one `SIGNUP_PROMO` entry per wallet.<br>• Idempotency key `promo:signup:<user_public_id>`.<br>• Concurrent logins (2 sessions, same instant) produce exactly one entry. |
| FR-AUTH-04.3 | The grant is logged internally with metadata: date/time, source `promo`, quantity, user ID. | SRS | Must | M4 | • Ledger entry `entry_type=SIGNUP_PROMO`, `amount=+10`, `created_at`, user/wallet, `balance_before=0`, `balance_after=10`, metadata `{"source": "promo"}`.<br>• Entry is part of the hash chain (NFR-SEC-02.2). |
| FR-AUTH-04.4 | Only one promo per verified identity: a verified email or phone already used by another account that received the promo makes the new account ineligible. | Derived (GAP-06) | Must | M4 | • Eligibility check uses blind indexes of verified email and phone.<br>• Ineligible accounts get 0 credits and a fraud signal (FR-OPS-04). |
| FR-AUTH-04.5 | The new balance is visible immediately in the header and dropdown. | Derived | Should | M4 | • After the granting login, the first rendered page shows 10. |

```gherkin
Scenario: Promo credits on first verified login
  Given a user registered and verified their email
  And the user has never received SIGNUP_PROMO
  When the user logs in
  Then the wallet balance is 10
  And exactly one SIGNUP_PROMO ledger entry exists with amount +10 and source "promo"

Scenario: No promo before verification
  Given an unverified user
  When the user logs in
  Then the wallet balance is 0 and no SIGNUP_PROMO entry exists

Scenario: Repeat and concurrent logins
  Given a verified user who already received SIGNUP_PROMO
  When the user logs in again from two devices at the same time
  Then the balance does not change and still exactly one SIGNUP_PROMO entry exists
```

### FR-AUTH-05 — Login, hashing, sessions, password reset (SRS §3.4)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| FR-AUTH-05.1 | Users log in with email and password. Unverified users may log in but stay restricted (FR-AUTH-03.4). | SRS | Must | M1 | • Wrong credentials give one generic message (no account enumeration).<br>• `next` redirect only to same-site URLs. |
| FR-AUTH-05.2 | Users who signed up with a social provider log in through that provider. | SRS | Could | M1 stretch / Post-MVP | • Depends on FR-AUTH-02. |
| FR-AUTH-05.3 | Passwords are stored only as salted, adaptive hashes: Argon2id primary, bcrypt as fallback hasher. | SRS | Must | M1 | • `PASSWORD_HASHERS[0]` is Argon2; DB inspection shows `argon2$argon2id$…`.<br>• Legacy hashes upgraded on next login. |
| FR-AUTH-05.4 | Sessions are server-side, carried by a secure cookie. | SRS | Must | M1 | • Redis-backed `cached_db` sessions; cookie `Secure`, `HttpOnly`, `SameSite=Lax`, `__Host-` prefix.<br>• Session key rotated on login and privilege change.<br>• **Deviation from SRS:** no JWT for browser sessions (GAP-07). |
| FR-AUTH-05.5 | "Forgot password" sends a secure, single-use, time-limited reset link to the registered email. | SRS | Must | M1 | • Link expires in 1 h (**Assumption**) and works once.<br>• Same response whether or not the account exists.<br>• Rate-limited per email and IP. |
| FR-AUTH-05.6 | A password reset or change invalidates all other sessions and notifies the user by email. | Derived (GAP-49) | Must | M1 | • Old session cookies on other devices are rejected after reset.<br>• "Your password was changed" email sent. |
| FR-AUTH-05.7 | Brute-force protection on login. | Derived | Must | M1 | • Failed attempts rate-limited per account and per IP (allauth rate limits + WAF rule).<br>• Lockout/backoff does not reveal whether the account exists. |

### FR-AUTH-06 — Role-based access control (HLRD §3.0)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| FR-AUTH-06.1 | Three core user types exist: **Renter**, **Lister**, **Staff**. Renter and Lister are capabilities of any verified account (one account can do both; Owner vs Agent is a per-listing tag). Staff has sub-roles Moderator, Support, Finance, Superadmin as Django groups. | HLRD + Derived (GAP-04) | Must | M1 | • Groups created by a data migration with fixed permission sets.<br>• A permission matrix test asserts every role × protected action. |
| FR-AUTH-06.2 | Authorisation is deny-by-default and enforced server-side in services and views. | HLRD | Must | M1 | • Every view has an explicit access rule; a test fails if a new URL lacks one. |
| FR-AUTH-06.3 | Object-level ownership: a lister can read/modify only their own listings, drafts, tag-change requests and analytics. | Derived | Must | M2 | • Accessing another user's object returns 404 (not 403).<br>• Automated IDOR tests for every lister URL. |
| FR-AUTH-06.4 | Staff accounts must use MFA before any ops-console access. | Derived (SRS §6.1 `mfa_enabled`, GAP-62) | Must | M1 | • allauth MFA (TOTP + recovery codes) enforced for `is_staff` users.<br>• Staff without MFA are redirected to MFA setup and cannot reach `/ops/`. |
| FR-AUTH-06.5 | Role and group changes are audited. | Derived | Must | M1 | • `AuditLog` row with actor, target user, old and new groups. |

---

## 3. Property management & listing (FR-LIST)

### FR-LIST-01 — Property submission (SRS §4.1)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| FR-LIST-01.1 | Only logged-in, verified users can create a listing. | SRS | Must | M2 | • Anonymous users are sent to log in with `next`; unverified users to verification (FR-AUTH-03.4). |
| FR-LIST-01.2 | Listing creation uses a guided multi-step form. | SRS | Must | M2 | • Six steps: Basics → Location → Details & price → Photos → Contact → Review & publish ([listings design §4.1](../design/05-listings-and-media.md#41-steps-and-fields)). |
| FR-LIST-01.3 | Listers can save progress as a draft and resume later. | SRS | Should | M2 | • Drafts are saved server-side from creation; autosave and "Save draft" on every step.<br>• "Continue" from My Properties opens the first incomplete step.<br>• Draft limits and retention per listings design §3 and §4.4. |
| FR-LIST-01.4 | The form performs robust client-side validation of required fields before server submission. | SRS | Must | M2 | • HTML5 constraints + Alpine.js inline messages on blur for every rule in listings design §4.3.<br>• Submit with errors is blocked client-side and focus moves to an error summary. |
| FR-LIST-01.5 | The server re-validates everything regardless of client validation. | Derived | Must | M2 | • Posting directly (no JS, crafted request) with invalid data is rejected with field errors. |
| FR-LIST-01.6 | Publishing validates completeness and makes the listing public (or sends it to review if flagged). | Derived | Must | M2 | • Publish requires all mandatory fields, tag, ≥ 3 READY photos, geocoded location, verified contact phone.<br>• Result is `PUBLISHED`, or `PENDING_REVIEW` if automated checks flag it (OQ-19). |
| FR-LIST-01.7 | The lister confirms they are the owner or an authorised agent, that the tag is accurate, and accepts the listing terms. | Derived | Should | M2 | • Unticked declarations block publish; accepted terms version is stored. |

### FR-LIST-02 — Required fields and images (SRS §4.2)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| FR-LIST-02.1 | Property address is mandatory. | SRS | Must | M2 | • Structured address (country, line 1, city; region/postcode per country rules).<br>• Geocoded to a PostGIS `Point` (SRID 4326) or a lister-placed pin before publish. |
| FR-LIST-02.2 | Property type is mandatory, from a controlled list. | SRS | Must | M2 | • Enum per listings design §6.1 (final list: OQ-24). |
| FR-LIST-02.3 | Price (rent) is mandatory. | SRS | Must | M2 | • Stored as integer minor units + ISO-4217 currency derived from country; `> 0`; within per-currency bounds.<br>• Rent period monthly (default) or weekly (OQ-24). No floats anywhere. |
| FR-LIST-02.4 | Description is mandatory. | SRS | Must | M2 | • 80–5,000 characters after trim; plain text (HTML stripped). |
| FR-LIST-02.5 | A title is mandatory. | Derived (SRS §5.5 email needs "listing title") | Must | M2 | • 10–100 characters. |
| FR-LIST-02.6 | Images are mandatory: minimum 3, maximum 20 per listing. | SRS | Must | M2 | • Publish blocked below 3 READY images; the 21st upload is refused (enforced under a row lock, so parallel uploads cannot exceed 20).<br>• A published listing cannot drop below 3. |
| FR-LIST-02.7 | Contact information is mandatory. It is listing-level, defaults from the lister's profile, and is stored encrypted. | SRS + Derived (GAP-20) | Must | M2 | • Contact phone required and OTP-verified when it differs from the account phone; contact email optional (**Assumption**, OQ-37).<br>• Phone/email stored with field-level encryption (NFR-SEC-01.4). |
| FR-LIST-02.8 | Contact details are never exposed before a reveal. | Derived (GAP-20) | Must | M2 | • Contact values absent from listing HTML, JSON-LD, OG tags, HTMX fragments, sitemaps, search results, logs and analytics for anyone except the owner, staff with permission, and users who revealed it.<br>• Automated test greps rendered responses for the stored values. |
| FR-LIST-02.9 | Title and description may not contain contact details. | Derived (GAP-65) | Must | M2 | • Clear phone/email/URL matches block submission; obfuscated matches raise a moderation flag (listings design V-12, OQ-39). |
| FR-LIST-02.10 | Image uploads accept common formats efficiently. | SRS | Must | M2 | • Accepted: JPEG, PNG, WebP (HEIC per OQ-23). Others rejected with a clear message.<br>• Direct-to-S3 presigned upload with per-file progress; web workers never stream image bytes. |
| FR-LIST-02.11 | Maximum file size 5 MB per image. | SRS | Must | M2 | • 5 MiB enforced in the browser, in the presigned policy and server-side. |
| FR-LIST-02.12 | Aspect ratio is enforced. | SRS | Must | M2 | • Policy per [listings design §8.3](../design/05-listings-and-media.md#83-aspect-ratio-policy): landscape accepted or auto-cropped to 4:3/16:9; portrait and panoramas rejected server-side, with an in-browser crop option (OQ-23). |
| FR-LIST-02.13 | Thumbnails and responsive variants are generated automatically. | SRS | Must | M2 | • Variants `thumb`, `card`, `md`, `lg`, `og`, `email` produced as WebP/JPEG; `srcset` used on cards and gallery.<br>• Processing completes p95 ≤ 30 s per image (**Assumption**). |
| FR-LIST-02.14 | Every image is verified and sanitised. | Derived (GAP-21) | Must | M2 | • Pillow decode/verify; non-images, polyglots and decompression bombs rejected.<br>• All metadata (EXIF incl. GPS, XMP, IPTC) stripped from served variants.<br>• Originals never served publicly. |
| FR-LIST-02.15 | Listers can order photos, choose the cover and add alt text. | Derived | Should | M2 | • Drag-and-drop plus keyboard-accessible "Move earlier/later", "Make cover"; alt text ≤ 150 chars with generated fallback. |

### FR-LIST-03 — Lister tag (SRS §4.3, CRITICAL)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| FR-LIST-03.1 | The listing form requires exactly one of two exclusive tags: **AgentListed** or **OwnerListed**. | SRS | Must | M2 | • Radio group with no default; publish blocked without a tag.<br>• DB CHECK: non-draft listings have a tag. |
| FR-LIST-03.2 | The tag is stored as listing metadata used for display, filtering and analytics. | SRS | Must | M2 | • `lister_tag` column (`AGENT_LISTED`/`OWNER_LISTED`), indexed for search filters (FR-LIST-05.5). |
| FR-LIST-03.3 | After first publish, the tag cannot be modified through any normal path. | SRS | Must | M2 | • Read-only in lister forms; service raises `ListerTagImmutableError`.<br>• DB trigger rejects `UPDATE` of `lister_tag` after first publish unless set by the approval service.<br>• Tag is editable while the listing has never been published (**Assumption**). |
| FR-LIST-03.4 | A tag change requires a formal administrative review: the lister files a `PropertyTagChangeRequest` (reason, optional evidence); a Moderator approves or rejects it. | SRS + Derived (GAP-22) | Must | M2→M6 | • One pending request per listing; 14-day cooldown after rejection.<br>• Approval changes the tag atomically with an `AuditLog` entry; rejection requires a note.<br>• Lister notified of either outcome.<br>• M2: admin action; M6: dedicated review queue (FR-OPS-03). |
| FR-LIST-03.5 | Tag changes do not affect existing reveals or ledger entries. | Derived | Must | M2 | • `ContactReveal` rows and ledger entries for the listing are unchanged after approval. |

```gherkin
Scenario: Tag required to publish
  Given a complete draft without a lister tag
  When the lister clicks Publish
  Then publishing fails with "Choose who is listing this property."

Scenario: Tag locked after publish
  Given a published listing tagged OwnerListed
  When the lister submits an edit that sets AgentListed
  Then the change is rejected and the tag is still OwnerListed

Scenario: Approved tag change
  Given a pending tag-change request from OwnerListed to AgentListed with a reason
  When a Moderator approves it with a note
  Then the listing tag is AgentListed
  And an AuditLog entry records actor, from, to and request id
  And the lister receives a decision notification
```

### FR-LIST-04 — Listing management and metrics (SRS §4.4)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| FR-LIST-04.1 | Users can view all properties they created, in every status, on the My Properties dashboard. | SRS | Must | M2 | • `/my/properties/` with status tabs (Live, In review, Drafts, Rented, Inactive) and counts. |
| FR-LIST-04.2 | Users can edit any property they created (all fields except the tag and country), via quick links. | SRS | Must | M2 | • "Edit" opens the step form; edits are audited; address change re-geocodes; contact phone change requires OTP before it takes effect.<br>• Optimistic concurrency: a stale edit returns 409. |
| FR-LIST-04.3 | Users can mark a published property as rented. | SRS | Must | M2 | • Confirmation dialog; status `RENTED`; removed from search within the cache TTL (≤ 60 s). |
| FR-LIST-04.4 | Users can unlist a published property, and relist a rented or unlisted one. | SRS (unlist) + Derived (relist) | Must | M2 | • Unlist → `UNLISTED`; relist re-runs publish checks.<br>• Inactive detail page shows "No longer available" to the public. |
| FR-LIST-04.5 | The dashboard provides intuitive status controls: only actions valid for the current status are shown. | SRS | Must | M2 | • Transitions follow the state machine in [listings design §9.1](../design/05-listings-and-media.md#91-state-machine); invalid transitions are rejected by the service. |
| FR-LIST-04.6 | Listings are never hard-deleted once published (they are archived), because reveals and ledger entries reference them. | Derived | Must | M2 | • "Delete" on a previously published listing sets `ARCHIVED`; FK `PROTECT` from ledger/reveals. |
| FR-LIST-04.7 | The dashboard shows per-listing **views**. | SRS | Must | M2→M6 | • Views = detail renders by non-owner, non-bot viewers, deduplicated per viewer per 30 min ([listings design §10.2](../design/05-listings-and-media.md#102-metric-definitions)). |
| FR-LIST-04.8 | The dashboard shows per-listing **saves**. | SRS | Must | M3 | • Current saved count (exact) from `SavedProperty` (FR-SAVE-01). |
| FR-LIST-04.9 | The dashboard shows per-listing **Show Number clicks** and successful **contact reveals**. | SRS | Must | M4 | • Clicks include insufficient-credit outcomes; reveals = distinct paid reveals. |
| FR-LIST-04.10 | Metrics are near-real-time. | SRS | Must | M2→M6 | • Counters visible ≤ 60 s after the event; saves and reveals immediately; dashboard refreshes by HTMX polling while visible.<br>• **Deviation from SRS:** "instantly" interpreted as ≤ 60 s (GAP-39, OQ-38). |
| FR-LIST-04.11 | Listings expire after a period without renewal, with a reminder. | Derived (GAP-45) | Should | M2 | • Default 60 days, reminder 7 days before, one-click renew (OQ-26). |
| FR-LIST-04.12 | Idle drafts are archived after a retention period. | Derived (GAP-45) | Should | M2 | • Default 90 days, reminder at day 80, images deleted (OQ-26). |

### FR-LIST-05 — Search and filter (SRS §4.5)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| FR-LIST-05.1 | Any website visitor (anonymous or logged in) can search published properties. | SRS | Must | M3 | • Search and results pages need no login. |
| FR-LIST-05.2 | Only `PUBLISHED` listings appear in results. | Derived | Must | M3 | • Drafts, review, rented, unlisted, expired, suspended and archived listings never appear (test per status). |
| FR-LIST-05.3 | Filter by location using geospatial queries. | SRS | Must | M3 | • Place text resolves to a point/area; radius options 2/5/10/25/50 km; PostGIS distance filter on a GiST index.<br>• Results are within the chosen radius (tested with fixtures at known distances). |
| FR-LIST-05.4 | Filter by price range (min and/or max). | SRS | Must | M3 | • Bounds inclusive; filter on monthly-equivalent rent in the market currency (GAP-42). |
| FR-LIST-05.5 | Filter by property type with multi-selection. | SRS | Must | M3 | • Several types combine with OR. |
| FR-LIST-05.6 | Filter by lister tag (AgentListed, OwnerListed, or both). | SRS | Must | M3 | • Multi-select; both or none selected = no tag filter. |
| FR-LIST-05.7 | Multi-selection filters combine predictably. | SRS | Must | M3 | • OR within one filter, AND across filters; documented in UI help and tested. |
| FR-LIST-05.8 | Sorting by newest and by price (low→high, high→low). | SRS | Must | M3 | • Stable tie-breaker; also Relevance (with a query) and Distance (with a location) (Derived). |
| FR-LIST-05.9 | Fuzzy (typo-tolerant) matching on text queries. | SRS | Must | M3 | • Trigram similarity on locality/title (e.g. "Bandra" ≈ "Bandara"), full-text on description; "Did you mean" for locality names. |
| FR-LIST-05.10 | Results are relevant and fast. | SRS | Must | M3 | • Meets NFR-PERF-01.1/01.2.<br>• Relevance: exact locality matches rank above fuzzy matches (golden-query test set). |
| FR-LIST-05.11 | Results are paginated. | Derived | Must | M3 | • 20 per page; page cap 50; total count shown (exact up to 10,000, then "10,000+"). |
| FR-LIST-05.12 | Search state is in the URL and works without JavaScript. | Derived | Should | M3 | • Filters in the query string; shareable; plain GET form works with JS disabled; HTMX enhances. |
| FR-LIST-05.13 | Helpful empty state. | Derived | Should | M3 | • Suggests widening radius, removing filters, spelling suggestions. |
| FR-LIST-05.14 | Property cards show cover image, price per period, title, locality, key facts, lister tag badge and save toggle. | Derived (SRS §11.1) | Must | M3 | • Card per UX spec; tag badge per NFR-UX-03. |

---

## 4. Credit consumption & lead generation (FR-CRED)

SRS §5.0: "the core monetization and lead generation mechanism." In MVP a **lead** is a paid contact reveal by a renter (GAP-01, OQ-01).

### FR-CRED-01 — Show Number visibility (SRS §5.1, CRITICAL)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| FR-CRED-01.1 | The primary CTA for accessing the lister's contact information on every listing detail page is labelled **"Show Number"**. | SRS | Must | M4 | • Exact label (translated in other locales). Cards link to the detail page (GAP-35). |
| FR-CRED-01.2 | The Show Number button is rendered only for logged-in, verified users with a positive balance (> 0). | SRS | Must | M4 | • Not present in the DOM for anonymous, unverified or zero-balance users. |
| FR-CRED-01.3 | The 2-credit cost is displayed adjacent to the button text. | SRS | Must | M4 | • Button reads "Show Number · 2 credits" (cost read from one setting `CREDITS_REVEAL_COST = 2`, OQ-43); the accessible name includes the cost. |
| FR-CRED-01.4 | Users not shown the button see a state-appropriate alternative. | Derived (GAP-05) | Must | M4 | • Anonymous: "Log in to view number" (→ login with `next`).<br>• Unverified: "Verify to view number".<br>• Balance 0: "Get credits to view number" (→ Purchase Credits). |
| FR-CRED-01.5 | The owner of the listing sees their own contact details and no Show Number button. | Derived (GAP-05) | Must | M4 | • No charge possible on own listing (service also rejects it). |
| FR-CRED-01.6 | A user who already revealed the listing sees the contact details directly, free. | Derived (GAP-05, SRS §5.4) | Must | M4 | • No button; contact shown with "Revealed on {date}". |
| FR-CRED-01.7 | Show Number is not offered on listings that are not `PUBLISHED`. | Derived (GAP-38) | Must | M4 | • Inactive listing page shows "No longer available"; reveal service rejects non-published listings. Prior revealers still see their contact. |

### FR-CRED-02 — Credit check (SRS §5.2, CRITICAL)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| FR-CRED-02.1 | On click, the system first verifies that the balance is ≥ 2 credits. | SRS | Must | M4 | • Balance 2 succeeds; balance 1 fails with FR-CRED-06 behaviour. |
| FR-CRED-02.2 | The check is atomic with the deduction: one database statement or one locked transaction, never read-then-write across statements without a lock. | SRS | Must | M4 | • Conditional `UPDATE … SET balance = balance - 2 WHERE id = :id AND balance >= 2 RETURNING balance` (or `SELECT … FOR UPDATE` then update) inside `transaction.atomic()`.<br>• 0 rows updated ⇒ `InsufficientCreditsError`, no ledger entry. |
| FR-CRED-02.3 | A negative balance is impossible. | SRS | Must | M4 | • DB `CHECK (balance >= 0)` on `CreditWallet`; a test that forces a direct negative update fails at DB level. |
| FR-CRED-02.4 | No unauthorised deductions: only the authenticated user's own wallet, via POST with CSRF, from a verified account. | SRS | Must | M4 | • GET never debits; cross-site POST rejected; another user's wallet cannot be targeted (wallet resolved from session, never from request input). |

### FR-CRED-03 — Credit deduction and ledger (SRS §5.3, CRITICAL)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| FR-CRED-03.1 | If the balance is sufficient, exactly 2 credits are deducted immediately, in the same request. | SRS | Must | M4 | • Balance after = before − 2; response renders the contact (FR-CRED-04.1). |
| FR-CRED-03.2 | Each deduction writes an immutable ledger entry with: unique transaction ID, user, balance before, balance after, timestamp, property ID, server process identity. | SRS | Must | M4 | • `CreditLedgerEntry`: `public_id` (UUID transaction ID), wallet/user, `entry_type=CONTACT_REVEAL`, `amount=-2`, `balance_before`, `balance_after`, `created_at` (UTC), `property` (FK; public ID shown), `process_info` = host/task ID + PID + request ID + release (GAP-33), idempotency key, `prev_hash`, `hash`. |
| FR-CRED-03.3 | Ledger entries are append-only. | SRS | Must | M4 | • DB trigger + role privileges reject `UPDATE`/`DELETE` on the ledger table (test proves both fail).<br>• Admin shows ledger read-only. Corrections only via `REVERSAL`/`ADMIN_ADJUSTMENT` entries. |
| FR-CRED-03.4 | A user is charged at most once per property. | Derived (GAP-05) | Must | M4 | • `ContactReveal` unique `(user, property)`; double click, retry or two tabs → one debit, one reveal. |
| FR-CRED-03.5 | Debit, reveal record and outbox message commit together or not at all. | Derived (GAP-10) | Must | M4 | • Fault injection after the debit (e.g. failing reveal insert) leaves balance, ledger, reveal and outbox unchanged. |

```gherkin
Scenario: Successful reveal
  Given a verified renter with 10 credits viewing a published listing they do not own
  When they click "Show Number · 2 credits"
  Then their balance is 8
  And one CONTACT_REVEAL ledger entry exists with amount -2, balance_before 10, balance_after 8 and the property id
  And the lister's contact details are displayed
  And the toast "Contact revealed. 2 credits deducted. Details emailed to you." is shown
  And one reveal email is queued for after commit

Scenario: Insufficient balance
  Given a verified renter with 1 credit
  When they click "Show Number · 2 credits"
  Then no credits are deducted and no ledger entry or reveal is created
  And a non-blocking message says 2 credits are needed and links to Purchase Credits

Scenario: Double click
  Given a verified renter with 10 credits
  When two reveal requests for the same listing arrive concurrently
  Then the balance is 8 and exactly one ContactReveal and one CONTACT_REVEAL entry exist

Scenario: Already revealed
  Given a renter who revealed the listing earlier
  When they open the listing again
  Then the contact is shown without a Show Number button and no credits are deducted

Scenario: Rollback means no email
  Given the reveal transaction fails after the debit statement
  Then the balance is unchanged and no reveal email is ever sent
```

### FR-CRED-04 — Contact display (SRS §5.4)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| FR-CRED-04.1 | Immediately after a successful deduction, the lister's phone number and/or email is displayed in a designated area (or confirmation dialog) on the listing page. | SRS | Must | M4 | • HTMX swap, no full page reload; contact rendered as `tel:`/`mailto:` links; focus moves to the revealed contact. |
| FR-CRED-04.2 | Revealed contacts remain accessible from the user's transaction history at no further cost. | SRS | Must | M4 | • Each `CONTACT_REVEAL` row has "View contact"; opening it never debits. Works after the listing is rented, unlisted, expired, suspended or archived. |
| FR-CRED-04.3 | Revisiting a revealed listing shows the contact free (FR-CRED-01.6). | Derived | Must | M4 | • Same as FR-CRED-01.6. |
| FR-CRED-04.4 | The contact purchased is retained as an encrypted snapshot on the reveal record. | Derived (GAP-34) | Must | M4 | • History shows the snapshot; if the listing is still published and the lister has since changed the contact, the current contact is also shown, free (OQ-13). |
| FR-CRED-04.5 | Revealed-contact responses are not cached. | Derived | Must | M4 | • `Cache-Control: no-store` on reveal responses and history contact views. |

### FR-CRED-05 — Automated email on deduction (SRS §5.5)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| FR-CRED-05.1 | Each successful deduction triggers an automated email to the user's registered email address. | SRS | Must | M4 | • Exactly one email per `ContactReveal`. If the email is unverified (phone-only verification), the email is held until the address is verified and the UI says so (GAP-26). |
| FR-CRED-05.2 | The email contains: property link, lister name, listing title, full description, the revealed contact details, and a transaction confirmation (transaction ID, credits deducted, balance after, date/time). | SRS + Derived (contact: GAP-36) | Must | M4 | • Template snapshot test checks every field; plain-text and HTML parts; no tracking pixels in transactional mail (**Assumption**). |
| FR-CRED-05.3 | The email is sent only after the deduction commits, via the transactional outbox. | SRS | Must | M4 | • `OutboxMessage` written in the reveal transaction; Celery sends after commit; target p95 ≤ 60 s from commit to provider acceptance.<br>• **Deviation from SRS:** "concurrently" becomes "after commit, asynchronously" (GAP-10). |
| FR-CRED-05.4 | Delivery uses a highly reliable, monitored transactional email service. | SRS | Must | M4 | • django-anymail (SES or Mailgun, OQ-32); retries with exponential backoff; provider delivery/bounce events stored; alert when failures > 2 % over 15 min; SPF/DKIM/DMARC pass. |
| FR-CRED-05.5 | Email sending is idempotent. | Derived | Must | M4 | • Outbox dedupe key per reveal; redelivered tasks never send twice. |

### FR-CRED-06 — Insufficient credit (SRS §5.6)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| FR-CRED-06.1 | If the user has fewer than 2 credits when attempting a reveal, a non-disruptive in-app notification is shown (toast or alert bar) and nothing is deducted. | SRS | Must | M4 | • No navigation, no modal, page state kept.<br>• Covers balance 1 and the race where the balance dropped after the page loaded. |
| FR-CRED-06.2 | The message is concise and states the required amount. | SRS | Must | M4 | • Copy: "You need 2 credits to view this number. Your balance is {n}." |
| FR-CRED-06.3 | The message has a direct, high-contrast link to Purchase Credits. | SRS | Must | M4 | • Link text "Buy credits"; contrast ≥ 4.5:1; goes to `/credits/buy/` (placeholder until M5). |
| FR-CRED-06.4 | The notification is accessible. | Derived (SRS §12) | Must | M4 | • `role="status"`/`aria-live`; not auto-dismissed in under 10 s or while focused/hovered; dismissible by keyboard. |

### FR-CRED-07 — Wallet and ledger foundation (Derived)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| FR-CRED-07.1 | Every user has exactly one `CreditWallet`, created automatically with the account. There is no "wallet setup" step. | Derived (GAP-53) | Must | M4 | • Unique wallet per user; backfill migration for existing users. |
| FR-CRED-07.2 | Credits are integers. | Derived | Must | M4 | • Integer columns only; no fractional credits anywhere. |
| FR-CRED-07.3 | Every balance change goes through `credits.services.grant_credits` / `debit_credits` with an entry type and idempotency key. | Derived | Must | M4 | • Entry types: `SIGNUP_PROMO`, `PURCHASE`, `CONTACT_REVEAL`, `ADMIN_ADJUSTMENT`, `REVERSAL`.<br>• Lint/import rule: no other module writes `CreditWallet.balance`. |
| FR-CRED-07.4 | The debit design is generic, so another consumption model (e.g. lister-pays lead unlock) can be added without changing the wallet/ledger schema. | Derived (GAP-01) | Must | M4 | • Adding an entry type is a choices change plus a new service caller; documented in an ADR. |
| FR-CRED-07.5 | Ledger balance invariant: wallet balance equals the sum of its ledger amounts, and each entry's `balance_after` equals the next entry's `balance_before`. | Derived (SRS §9.2) | Must | M4 | • Property-based test over random grant/debit sequences; nightly audit (NFR-SEC-02.4). |

### FR-CRED-08 — Reveal abuse protection (Derived)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| FR-CRED-08.1 | Reveals are rate-limited per user. | Derived (GAP-66) | Must | M4 | • Configurable hourly/daily limits (defaults in the security design; OQ-35); excess returns a clear 429 message with no debit. |
| FR-CRED-08.2 | Reveal velocity and patterns feed fraud signals. | Derived | Should | M4→M6 | • Events recorded for FR-OPS-04 rules. |
| FR-CRED-08.3 | Contact values never appear in logs, error reports or analytics. | Derived | Must | M4 | • Log redaction test; Sentry `send_default_pii=False` with scrubbing. |

---

## 5. Credit management & purchase (FR-PAY)

### FR-PAY-01 — Purchase access (SRS §6.1)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| FR-PAY-01.1 | Purchasing credits is prominently accessible through a dedicated **"Purchase Credits"** tab in the Profile Icon Dropdown. | SRS | Must | M1 (link) → M5 | • Tab present for every logged-in user; leads to `/credits/buy/`. |
| FR-PAY-01.2 | The purchase flow needs minimal steps on desktop and mobile. | SRS | Should | M5 | • From dropdown to gateway in ≤ 3 interactions (choose package → choose method → pay); no account data re-entry. |
| FR-PAY-01.3 | The payment funnel is seamless and responsive (mobile-first). | SRS | Must | M5 | • Works at 320 px width; touch targets ≥ 44 px; return from gateway lands on a status page that resolves automatically (FR-PAY-04.4). |
| FR-PAY-01.4 | The database schema is designed for transactional integrity and speed. | SRS | Must | M4–M5 | • FK constraints, CHECK constraints, unique idempotency constraints and indexes for every hot query path (reviewed in the data-model design). |
| FR-PAY-01.5 | The user record exposes last-login time and MFA-enabled status. | SRS (stray §6.1 text, kept) | Must | M1 | • Django `last_login` populated on login; `mfa_enabled` derived from allauth MFA authenticators (GAP-02). |
| FR-PAY-01.6 | `Menu_Items` table with `allergy_flags`. | SRS (copy-paste error) | Won't | — | • Withdrawn: belongs to another project (GAP-02). |

### FR-PAY-02 — Credit packages and localised pricing (SRS §6.2)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| FR-PAY-02.1 | The system offers multiple distinct credit packages. | SRS | Must | M5 | • ≥ 3 active packages; seed 20, 50, 120 credits (OQ-03). |
| FR-PAY-02.2 | Each package has an associated price. | SRS | Must | M5 | • A package without a price in the resolved currency is not offered in that currency. |
| FR-PAY-02.3 | Packages incorporate volume discounts: price per credit decreases as package size increases. | SRS | Should | M5 | • Saving a price book where a larger package's per-credit price is ≥ a smaller one's is rejected (per currency).<br>• UI shows per-credit price and "Save X %" against the smallest package. |
| FR-PAY-02.4 | Prices are displayed in the user's localised currency, determined by account region setting or, failing that, IP geolocation. | SRS | Should | M5 | • Resolution order: account region/currency setting → GeoIP country (MaxMind GeoLite2) → market default.<br>• Only currencies present in the price book are offered. |
| FR-PAY-02.5 | Localised prices come from an explicit per-currency price book managed by Finance, not live FX conversion. | Derived (GAP-13) | Must | M5 | • `CreditPackagePrice(package, currency, amount_minor, valid_from, valid_to)`; edits audited; no deploy needed. |
| FR-PAY-02.6 | The charged currency and amount equal the displayed ones. | Derived | Must | M5 | • `PaymentOrder` snapshots package, credits, `amount_minor`, currency at creation; gateway session uses those values. |
| FR-PAY-02.7 | Money is stored as integer minor units plus ISO-4217 currency and formatted per locale. | Derived | Must | M5 | • No floats; JPY (0 decimals) and KWD (3 decimals) tested. |

### FR-PAY-03 — Payment gateway integration (SRS §6.3)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| FR-PAY-03.1 | At least two major, globally recognised gateways are integrated: **Stripe** (Checkout) and **PayPal** (Orders v2). | SRS | Must | M5 | • A purchase completes end-to-end with each gateway in sandbox and (once) live. |
| FR-PAY-03.2 | Card and digital-wallet payments are supported. | SRS | Must | M5 | • Cards (and Apple Pay / Google Pay where Stripe enables them) via Stripe; PayPal balance/cards via PayPal. |
| FR-PAY-03.3 | Payment data is handled by tokenisation through hosted checkout; no card data enters our systems. | SRS | Must | M5 | • No card input fields on our domain; see NFR-SEC-03. |
| FR-PAY-03.4 | Webhooks drive fulfilment, status updates and error handling. | SRS | Must | M5 | • Signature verified for every event; invalid signature → 400 and alert metric.<br>• Each event stored once in `PaymentWebhookEvent` (unique gateway + event ID); processing idempotent. |
| FR-PAY-03.5 | Gateways sit behind a `PaymentGateway` interface; further adapters (e.g. Razorpay) can be added without changing callers. | Derived (GAP-14) | Should | M5 | • Shared contract test suite passes for every adapter. Razorpay adapter optional (OQ-07). |
| FR-PAY-03.6 | Failed, cancelled or declined payments are handled promptly and clearly. | SRS | Must | M5 | • User sees a reason category (not raw gateway text), "Try again" and the other gateway; order marked FAILED/CANCELLED; no credits granted. |

### FR-PAY-04 — Instant allocation (SRS §6.4, CRITICAL)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| FR-PAY-04.1 | Purchased credits are allocated within 5 seconds of successful payment confirmation. | SRS | Must | M5 | • `payment_fulfillment_latency_seconds` p99 ≤ 5 s, measured from our receipt of the gateway confirmation (webhook or verified return) to the committed `PURCHASE` entry. |
| FR-PAY-04.2 | Credits are applied only after the gateway confirms the payment server-to-server: either a signature-verified webhook **or** a server-side API verification of the payment on the success redirect. Client-side signals alone never grant credits. | SRS | Must | M5 | • Forged success redirect without a paid gateway payment grants nothing.<br>• **Deviation from SRS:** webhook-only verification is widened to "webhook or server-side API verification" (GAP-09). |
| FR-PAY-04.3 | Fulfilment is exactly-once per gateway payment. | Derived (GAP-09) | Must | M5 | • Unique `(gateway, gateway_payment_id)`; idempotency key `pay:<gateway>:<gateway_payment_id>`; webhook + redirect racing → one `PURCHASE` entry. |
| FR-PAY-04.4 | The visible balance updates without a manual reload. | SRS | Must | M5 | • Return page polls order status (HTMX, 1 s) and shows the new balance as soon as fulfilled; header badge updated out-of-band. |
| FR-PAY-04.5 | Amount, currency and order reference are checked against the `PaymentOrder` before fulfilment. | Derived | Must | M5 | • Mismatch → no credits, order flagged for Finance, alert. |
| FR-PAY-04.6 | Stuck and mismatched payments are reconciled automatically. | Derived (GAP-09) | Must | M5 | • Every 5 min, orders pending > 10 min are re-verified with the gateway; daily gateway vs orders vs ledger reconciliation; mismatches alert. |

```gherkin
Scenario: Webhook arrives first
  Given a PENDING PaymentOrder for 50 credits
  When a valid "payment succeeded" webhook arrives
  Then one PURCHASE ledger entry of +50 is committed within 5 seconds
  And the order is FULFILLED

Scenario: Redirect arrives before the webhook
  Given a PENDING PaymentOrder
  When the user returns on the success URL and the server confirms the payment with the gateway API
  Then credits are allocated
  And the later webhook is recorded but grants nothing more

Scenario: Forged success redirect
  Given a PENDING PaymentOrder that the gateway reports as unpaid
  When the success URL is requested
  Then no credits are granted and the page shows "Payment not confirmed yet"
```

### FR-PAY-05 — Transaction history (SRS §6.5)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| FR-PAY-05.1 | Users can view a detailed history of all credit purchases and consumption events (and promo, adjustment and reversal entries). | SRS | Must | M4 (consumption) → M5 (purchases) | • Every ledger entry of the user appears exactly once. |
| FR-PAY-05.2 | Each row shows date, time, credit amount (+/−) and a descriptive label. | SRS | Must | M4 | • Time in the user's timezone; labels: "Welcome credits", "Purchased 50 credits", "Contact revealed: {title}", "Adjustment", "Reversal"; also balance after. |
| FR-PAY-05.3 | Purchases are visually distinct and show the payment method. | SRS | Must | M5 | • Method from gateway data: card brand + last 4, or "PayPal"; purchase rows styled differently (not by colour alone). |
| FR-PAY-05.4 | Consumption rows reference the associated property ID and link to it and to the free contact view. | SRS | Must | M4 | • Property public ID and title; "View contact" (FR-CRED-04.2). |
| FR-PAY-05.5 | The history is filterable. | SRS | Must | M4 | • Filters: type (purchase, consumption, promo, adjustment/reversal) and date range; filters in URL. |
| FR-PAY-05.6 | The history is paginated, newest first. | Derived | Should | M4 | • 25 rows per page; p95 ≤ 300 ms for users with 10,000 entries (**Assumption**). |
| FR-PAY-05.7 | Purchase receipts can be viewed and are emailed after fulfilment. | Derived | Should | M5 | • Receipt shows order ID, package, credits, amount, currency, method, date, merchant details. |

### FR-PAY-06 — Refunds, chargebacks and reconciliation (Derived)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| FR-PAY-06.1 | Gateway refund and dispute events create `REVERSAL` entries for the purchased credits, never pushing the balance below 0. | Derived (GAP-31) | Should | M5 | • Shortfall recorded and the account flagged for Finance (FR-OPS-06). |
| FR-PAY-06.2 | Refund policy is applied consistently. | Derived (GAP-31) | Should | M5 | • No self-service refunds in MVP; Finance-initiated refunds through the gateway only (OQ-05). |
| FR-PAY-06.3 | Live gateway configuration is verified before launch. | Derived | Should | M7 | • One real low-value transaction per gateway, then refunded. |

---

## 6. Profile & account management (FR-PROF)

### FR-PROF-01 — Profile icon and dropdown access (SRS §7.0, §7.1, CRITICAL)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| FR-PROF-01.1 | A Profile Icon (avatar or silhouette) sits at the top-right of the header for logged-in users on every page. | SRS | Must | M1 | • Present on all authenticated layouts including mobile. |
| FR-PROF-01.2 | Clicking or tapping the icon reveals a dropdown menu. | SRS | Must | M1 | • Disclosure button with `aria-expanded`; opens on click, tap, Enter and Space. |
| FR-PROF-01.3 | The dropdown shows the user's name or email, and immediately below it the current credit balance, prominently at the top. | SRS | Must | M1 (name) → M4 (balance) | • Order: name/email → balance ("{n} credits") → tabs. |
| FR-PROF-01.4 | The dropdown is the central navigation hub for account and monetisation settings. | SRS | Must | M1 | • All account pages reachable from it (FR-PROF-02.1). |
| FR-PROF-01.5 | The dropdown is "persistent": it stays open until the user dismisses it and is available on every page. | SRS | Should | M1 | • Closes on Escape, outside click or selection; not on hover-out (GAP-47). |

### FR-PROF-02 — Dropdown tabs (SRS §7.2, CRITICAL)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| FR-PROF-02.1 | The dropdown contains at least: **Profile**, **My Properties**, **Purchase Credits**; plus Transaction history and Saved properties (Derived); **Logout** at the bottom. | SRS + Derived | Must | M1 → M5 | • Items in this order; each a real link. |
| FR-PROF-02.2 | Profile: users can view and edit Name, Email, Phone and Password. | SRS | Must | M1 | • Profile page shows current values (phone masked except last digits). |
| FR-PROF-02.3 | Profile edits use robust form validation (client and server). | SRS | Must | M1 | • Inline errors; server authoritative; changes audited. |
| FR-PROF-02.4 | Changing email is a secure two-step process. | SRS | Must | M1 | • Re-authentication (≤ 10 min window) → confirmation sent to the new address → switch only after confirmation → notice to the old address (GAP-48). |
| FR-PROF-02.5 | Changing password is a secure two-step process. | SRS | Must | M1 | • Current password (re-auth) + new password confirmation; other sessions invalidated; email notice (FR-AUTH-05.6). |
| FR-PROF-02.6 | Changing phone requires OTP verification of the new number before it takes effect. | Derived (GAP-48) | Should | M1 | • Old number stays active until the new one is verified. |
| FR-PROF-02.7 | Users manage communication and email-notification preferences (e.g. promotional alerts). | SRS | Must | M1 | • `NotificationPreference`; promotional opt-in default **off** (**Assumption**); transactional emails always on and labelled; one-click unsubscribe in promotional mail. |
| FR-PROF-02.8 | My Properties opens the listing-management dashboard (FR-LIST-04). | SRS | Must | M2 | • Link works for users with zero listings (empty state with "List your property"). |
| FR-PROF-02.9 | My Properties shows quick statistics: listing views, contact reveals, overall performance metrics. | SRS | Must | M4 → M6 | • 30-day summary strip (views, saves, Show Number clicks, reveals, live listings); per-listing analytics drill-down with chart and accessible table (M6). |
| FR-PROF-02.10 | Purchase Credits opens the purchase workflow. | SRS | Must | M5 | • Same as FR-PAY-01.1. |
| FR-PROF-02.11 | The purchase page dynamically presents the active packages with pricing and volume discounts, and selecting one initiates the secure payment flow. | SRS | Must | M5 | • Packages from the price book (FR-PAY-02); selection → gateway choice → hosted checkout. |

### FR-PROF-03 — Logout (SRS §7.3)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| FR-PROF-03.1 | A clear, distinct "Logout" option is at the bottom of the dropdown. | SRS | Must | M1 | • Visually separated; last item. |
| FR-PROF-03.2 | Logout terminates the session on the server. | SRS | Must | M1 | • Session row/cache entry deleted; replaying the old cookie gives an anonymous request. |
| FR-PROF-03.3 | Logout invalidates all active authentication tokens of the current login and any "remember me" state; users can also sign out all other sessions. | SRS | Must | M1 | • "Sign out of all devices" via allauth user sessions; password change does it automatically (GAP-49). |
| FR-PROF-03.4 | Logout clears local authentication artefacts. | SRS | Must | M1 | • Cookies expired; `Clear-Site-Data: "cache", "cookies", "storage"`; authenticated pages sent `Cache-Control: no-store` so Back shows nothing private. |
| FR-PROF-03.5 | Logout is a POST with CSRF protection. | Derived | Must | M1 | • GET `/logout/` does not log out. |

---

## 7. Derived functional requirements (not in the SRS)

### FR-SAVE-01 — Saved properties (Derived, GAP-19)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| FR-SAVE-01.1 | Verified users can save and unsave a property from cards and the detail page. | Derived | Must | M3 | • Toggle with `aria-pressed`; anonymous click → login with `next`, save completed after login. |
| FR-SAVE-01.2 | Users see their saved properties on a dedicated page. | Derived | Must | M3 | • `/account/saved/`, newest first; inactive listings shown as "No longer available". |
| FR-SAVE-01.3 | One save per user and property; saves feed the listing "saves" metric. | Derived | Must | M3 | • Unique `(user, property)`; FR-LIST-04.8 counts match. |

### FR-OPS — Ops console (Derived from diagram "Ops Console", GAP-18)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| FR-OPS-01.1 | The staff console (hardened Django admin + custom staff views) is reachable only at a non-default path by MFA-enabled staff with group permissions. | Derived | Must | M1→M6 | • `/ops/…`; staff idle timeout 30 min; optional IP allow-list (OQ-41). |
| FR-OPS-01.2 | Every staff change is audited; financial records are read-only in the console. | Derived | Must | M6 | • `AuditLog` for each change; ledger, orders, webhook events have no edit/delete permissions. |
| FR-OPS-02.1 | Moderators work a queue of moderation cases (user reports, automated flags) with actions: dismiss, request changes, suspend listing, restore. | Derived | Must | M6 | • Suspended listings leave search and block new reveals; lister notified; every action audited. |
| FR-OPS-02.2 | Renters can report a listing (reason + optional note). | Derived | Should | M6 | • Report creates/updates a `ModerationCase`; rate-limited per user. |
| FR-OPS-03.1 | Moderators review tag-change requests in a dedicated queue (age, SLA, evidence via short-lived signed URLs, lister history). | Derived (SRS §4.3) | Must | M6 | • Decision within SLA (default 2 business days, OQ-18) visible in queue. |
| FR-OPS-04.1 | Automatic fraud flags: reveal velocity, multiple accounts per device/IP/phone, promo-only accounts with immediate reveals, chargebacks, duplicate contacts or images across owners. | Derived (diagram "fraud review") | Should | M6 | • Thresholds configurable; flags open cases; no automatic bans in MVP. |
| FR-OPS-05.1 | Staff can monitor background jobs: queue depth, oldest message age, outbox pending/failed with retry, last beat run, failed tasks. | Derived (diagram "monitor & manage jobs") | Should | M6 | • Page backed by metrics; failed outbox message can be retried by Superadmin. |
| FR-OPS-06.1 | Finance has a ledger-audit dashboard: audit runs, mismatches, chain status, per-wallet re-run. | Derived (SRS §9.2) | Must | M6 | • Shows the last nightly run; any mismatch is red and linked to an incident. |
| FR-OPS-06.2 | Admin credit adjustments need four-eyes approval and a reason. | Derived | Must | M6 | • Requester ≠ approver (enforced); result is an `ADMIN_ADJUSTMENT` entry. |
| FR-OPS-06.3 | Finance/Support can look up payment orders and trigger an idempotent re-verification with the gateway. | Derived | Should | M6 | • Order timeline (events, webhooks, ledger). |
| FR-OPS-07.1 | Support can look up a user with PII masked by default; unmasking needs a reason and is audited. | Derived | Should | M6 | • Search by exact email (blind index) or public ID; actions: resend verification, revoke sessions, view wallet summary. |

### FR-NOTIF-01 — Transactional notification infrastructure (Derived)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| FR-NOTIF-01.1 | All transactional email and SMS go through provider-agnostic adapters (django-anymail; Twilio) fed by the outbox. | Derived (SRS §5.5, diagram) | Must | M1 | • Provider switch is configuration only. |
| FR-NOTIF-01.2 | Every send is logged (template, recipient pseudonym, status, provider ID); bounces and complaints suppress further non-essential sends. | Derived | Should | M1 | • `NotificationLog`; suppression list honoured. |
| FR-NOTIF-01.3 | Email templates are translatable and render correctly in major clients. | Derived | Should | M1 | • Plain-text part present; images via `email` variants (JPEG). |

### FR-LEAD-01 — Inquiry leads and lister-pays unlock (Derived from flow chart, **Post-MVP**, OQ-01, OQ-21, OQ-17)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| FR-LEAD-01.1 | Renters can send a free inquiry/contact request to a lister. | Derived (DIA) | Won't (MVP) | Post-MVP | • To be specified if OQ-21 is accepted. |
| FR-LEAD-01.2 | Listers are notified of new leads (email/SMS). | Derived (DIA) | Won't (MVP) | Post-MVP | • OQ-17. |
| FR-LEAD-01.3 | Listers pay credits to unlock a lead's contact. | Derived (DIA) | Won't (MVP) | Post-MVP | • Uses FR-CRED-07.4 (new entry type, same services). |

### FR-KYC-01 — Owner and listing verification (Derived from diagram, **Post-MVP**, OQ-20)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| FR-KYC-01.1 | Owners can verify identity through a Verification API. | Derived (DIA) | Won't (MVP) | Post-MVP | • Provider adapter in `apps.verification`. |
| FR-KYC-01.2 | Listers can upload ownership proofs / KYC documents for staff review. | Derived (DIA) | Won't (MVP) | Post-MVP | • Private bucket, malware scan, signed URLs ≤ 5 min. |
| FR-KYC-01.3 | MVP keeps the hooks: private-documents bucket and the tag-change evidence upload use the same storage path and access controls. | Derived | Should | M2 | • Evidence files never public; access audited. |
| FR-KYC-01.4 | Verified badges on listings/listers. | Derived (DIA) | Won't (MVP) | Post-MVP | • Depends on FR-KYC-01.1. |

---

## 8. Non-functional requirements

### NFR-PERF-01 — Latency (SRS §8.1)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| NFR-PERF-01.1 | Property search requests complete within **500 ms** under standard load. | SRS | Must | M3, verified M7 | • Server-side p95 ≤ 500 ms (ALB target response time + OTel span) on a prod-like dataset (≥ 500k listings, **Assumption**).<br>• "Standard load" per OQ-09; until answered, architecture §1.1 assumption. |
| NFR-PERF-01.2 | Property search requests do not exceed **1,000 ms** at peak load. | SRS | Must | M3, verified M7 | • Server-side p95 ≤ 1,000 ms at peak load; error rate < 0.1 %. |
| NFR-PERF-01.3 | Credit transactions (Show Number reveal; our side of purchase start and fulfilment) complete within **500 ms** under standard load. | SRS | Must | M4/M5, verified M7 | • p95 ≤ 500 ms for `reveal_contact` and `fulfill_order`; gateway-hosted time excluded (GAP-55). |
| NFR-PERF-01.4 | Credit transactions do not exceed **1,000 ms** at peak load. | SRS | Must | M4/M5, verified M7 | • p95 ≤ 1,000 ms at peak (including 1,000 debits/s, NFR-PERF-02.1). |
| NFR-PERF-01.5 | Performance relies on optimised indexing, read replicas and CDN caching for static assets. | SRS | Must | M0–M3 | • EXPLAIN plans of canonical queries use indexes (no seq scans on large tables, checked in CI/nightly).<br>• Search reads routed to the replica; static/media served via CloudFront. |
| NFR-PERF-01.6 | Front-end performance supports the "high-speed response" intent on mobile. | Derived | Should | M0→M7 | • Core Web Vitals p75 mobile: LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1; Lighthouse CI budgets. |

### NFR-PERF-02 — Concurrency (SRS §8.2)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| NFR-PERF-02.1 | The credit deduction mechanism handles **1,000 transactions per second** without data inconsistency. | SRS | Must | M0 spike, M4, M7 | • k6/Locust on prod-like staging: ≥ 1,000 reveals/s across distinct wallets for ≥ 10 min (15 min in M7).<br>• Afterwards the ledger audit reports 0 mismatches and 0 negative balances. |
| NFR-PERF-02.2 | No race conditions on a single wallet. | SRS | Must | M4 | • Hot-wallet test: 200 concurrent reveals (distinct listings) on a wallet with 20 credits → exactly 10 succeed, balance 0, 10 ledger entries. |
| NFR-PERF-02.3 | No degradation of service at that rate. | SRS | Must | M4, M7 | • p95 within NFR-PERF-01.3/01.4; error rate < 0.1 %; no DB connection exhaustion. |
| NFR-PERF-02.4 | Concurrency control uses PostgreSQL short transactions with row-level locking / conditional updates at READ COMMITTED, DB constraints and unique keys. No Kafka or external queue in the debit path. | SRS (mechanism examples) | Must | M4 | • ADR-0005 accepted; design review confirms.<br>• **Deviation from SRS:** the SRS examples (serializable, optimistic locking, Kafka) are replaced by a simpler mechanism that meets the same goal (GAP-08). |
| NFR-PERF-02.5 | Grants (promo, purchase, adjustment, reversal) use the same concurrency-safe services. | Derived | Must | M4/M5 | • Concurrent grant + debit on one wallet keep the balance invariant (FR-CRED-07.5). |

### NFR-AVAIL-01 — Availability, backup and recovery (SRS §8.3)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| NFR-AVAIL-01.1 | Automated database backups with point-in-time recovery. | Derived (SRS §8.3 presumes backups) | Must | M0 (dev) → M7 | • RDS automated backups + PITR, retention ≥ 14 days (**Assumption**); snapshots encrypted. |
| NFR-AVAIL-01.2 | Backup restoration is tested regularly to prove backups are viable and uncorrupted. | SRS | Must | M7, then quarterly | • Restore to a new instance; app smoke tests and the ledger audit pass on the restored DB; drill report filed. |
| NFR-AVAIL-01.3 | Detailed runbooks exist for common incidents, including payment API failure and database performance degradation. | SRS | Must | M7 | • Runbooks also for webhook backlog, Redis outage, email/SMS outage, ledger mismatch, Celery backlog, credential stuffing, deploy rollback, restore. Each has detection, triage, mitigation, comms, verification; each rehearsed once. |
| NFR-AVAIL-01.4 | Monthly availability target **99.9 %** (proposed). | Derived (GAP-16) | Must | M7 | • Measured by synthetic checks and ALB 5xx; confirmation OQ-08. |
| NFR-AVAIL-01.5 | **RPO ≤ 5 min** (proposed). | Derived (GAP-16) | Must | M7 | • Demonstrated in the restore drill. |
| NFR-AVAIL-01.6 | **RTO ≤ 1 h** (proposed). | Derived (GAP-16) | Must | M7 | • Demonstrated in the restore drill. |
| NFR-AVAIL-01.7 | No single point of failure in the request path; zero-downtime deploys. | Derived | Should | M7 | • Multi-AZ RDS; ≥ 2 web tasks across AZs; rolling deploys with health-check rollback. |
| NFR-AVAIL-01.8 | Graceful degradation when a dependency fails. | Derived | Should | M5 | • One gateway down → the other stays available; email provider down → outbox retries; geocoder down → manual pin. |

### NFR-SEC-01 — Data encryption and PII (SRS §9.1)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| NFR-SEC-01.1 | All traffic is encrypted in transit with TLS 1.2 or higher. | SRS | Must | M0 | • TLS ≥ 1.2 at CloudFront and ALB; HSTS (1 year, includeSubDomains); TLS to RDS and ElastiCache; SSL Labs grade A. |
| NFR-SEC-01.2 | All stored data is encrypted at rest with AES-256. | SRS | Must | M0 | • KMS encryption on RDS (incl. replicas, snapshots), ElastiCache, S3, EBS/ephemeral storage, backups. |
| NFR-SEC-01.3 | Passwords are never stored or logged in recoverable form. | SRS | Must | M1 | • See FR-AUTH-05.3; log redaction test. |
| NFR-SEC-01.4 | Contact numbers and designated PII are additionally encrypted at application level (field-level AES-256-GCM). | SRS + Derived (GAP-12) | Must | M1–M2 | • DB snapshot inspection shows ciphertext for listing contact phone/email and user phone; keys in KMS with rotation. |
| NFR-SEC-01.5 | PII is tokenised or pseudonymised wherever possible. | SRS | Must | M1–M2 | • HMAC blind indexes for lookups (verified phone; login email per OQ-29); public UUIDs instead of sequential IDs; logs/analytics use pseudonymous IDs. |
| NFR-SEC-01.6 | Payment information is never stored beyond gateway references. | SRS | Must | M5 | • Only gateway IDs, brand and last 4 stored (NFR-SEC-03). |
| NFR-SEC-01.7 | PII and secrets never appear in logs, traces or error reports. | Derived | Must | M0 | • structlog redaction processor; Sentry scrubbing; sampled-log check in M7. |

### NFR-SEC-02 — Credit integrity (SRS §9.2)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| NFR-SEC-02.1 | The credit balance is stored and changed only through the credits services. | SRS | Must | M4 | • No raw writes elsewhere (import-linter rule); admin read-only; DB role used by the app cannot `UPDATE` ledger rows. |
| NFR-SEC-02.2 | Ledger entries form an immutable, cryptographically linked audit trail. | SRS | Must | M4 | • Per-wallet SHA-256 hash chain: `hash = SHA256(prev_hash ‖ canonical(entry))`; tampering with any entry breaks verification (test). |
| NFR-SEC-02.3 | Append-only enforcement at DB level (see FR-CRED-03.3). | SRS | Must | M4 | • Trigger + privileges. |
| NFR-SEC-02.4 | Regular internal audits compare every live balance with the ledger history. | SRS | Must | M4 | • Nightly job: balance = Σ amounts, last `balance_after` = balance, chain verifies; result stored per run. |
| NFR-SEC-02.5 | Discrepancies raise automated alerts. | SRS | Must | M4 | • Any mismatch pages on-call within 15 min of detection and appears on the ledger-audit dashboard (FR-OPS-06.1). |
| NFR-SEC-02.6 | Manual corrections are ledger entries with reason and four-eyes approval (FR-OPS-06.2). | Derived | Must | M6 | • No direct balance edits exist. |

### NFR-SEC-03 — Payment compliance (SRS §9.3)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| NFR-SEC-03.1 | Payment processing adheres to PCI DSS through certified gateways. | SRS | Must | M5 | • Stripe and PayPal are PCI DSS Level 1 providers; our scope is SAQ A; SAQ A completed before go-live. |
| NFR-SEC-03.2 | The application never stores, transmits or processes raw card data. | SRS | Must | M5 | • Hosted checkout only; no card fields on our pages; CSP restricts payment-related scripts; code review checklist item. |
| NFR-SEC-03.3 | Webhook endpoints are authenticated and hardened. | Derived | Must | M5 | • Signature verification, size limit, rate limit, CSRF-exempt only for these routes; secrets in Secrets Manager. |

### NFR-SEC-04 — Application security baseline (Derived)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| NFR-SEC-04.1 | The application meets OWASP ASVS Level 2 for in-scope controls. | Derived | Must | M0→M7 | • ASVS L2 checklist completed in M7; external pen test with no open Critical/High. |
| NFR-SEC-04.2 | Secure HTTP defaults. | Derived | Must | M0 | • CSP (nonce-based, no inline script), CSRF on all POSTs incl. HTMX, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`, secure cookies. |
| NFR-SEC-04.3 | Abuse rate limits on sensitive endpoints. | Derived | Must | M1–M4 | • Login, sign-up, OTP, password reset, reveal, search: app limits + WAF rate rules. |
| NFR-SEC-04.4 | Supply-chain and secret hygiene. | Derived | Must | M0 | • Locked dependencies with hashes; pip-audit, bandit, image scan, gitleaks in CI; secrets only in Secrets Manager. |

### NFR-SEC-05 — Privacy and data protection (Derived, GAP-51)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| NFR-SEC-05.1 | Users accept versioned Terms and Privacy Policy at sign-up; acceptance is stored. | Derived | Must | M1 | • Version and timestamp stored per user. |
| NFR-SEC-05.2 | Non-essential cookies/analytics need consent where the launch market requires it. | Derived | Should | M1 | • Depends on OQ-28; essential cookies only by default. |
| NFR-SEC-05.3 | A data map and retention schedule exist and are enforced by jobs. | Derived | Should | M7 | • Documented retention for drafts, logs, OTP records, webhook payloads, KYC (post-MVP). |
| NFR-SEC-05.4 | Data-subject rights (export, deletion) are supported as required by the launch markets. | Derived | Should | Post-MVP unless OQ-28 says otherwise | • Ledger and financial records retained (pseudonymised) where law requires. |

### NFR-SCAL-01 — Cloud native and IaC (SRS §10.1)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| NFR-SCAL-01.1 | The application is deployed on cloud-native managed services. | SRS | Must | M0 | • AWS ECS Fargate, RDS PostgreSQL, ElastiCache, S3, CloudFront, WAF, SES, Secrets Manager, KMS, CloudWatch. |
| NFR-SCAL-01.2 | Web and worker tiers scale horizontally without code changes. | SRS | Must | M0, verified M7 | • Stateless containers (sessions in Redis/DB, files in S3); autoscaling on CPU/requests and queue depth; scale-out test in M7. |
| NFR-SCAL-01.3 | The design serves global markets without major refactoring. | SRS | Must | M0 | • Multi-currency money model, timezone-aware datetimes (UTC storage), i18n-ready code (NFR-UX-07), CDN at the edge, region parameterised in IaC (OQ-33). |
| NFR-SCAL-01.4 | Infrastructure is defined as code for reproducible environments. | SRS | Should | M0 | • All AWS resources in Terraform (remote state with locking); dev/staging/prod from the same modules; `terraform plan` shows no drift. |
| NFR-SCAL-01.5 | Deployments are rapid and consistent. | SRS | Should | M0 | • GitHub Actions: one immutable image per commit promoted by digest; migration task; rolling deploy with automatic rollback. |

### NFR-CODE-01 — Code standards (SRS §10.2)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| NFR-CODE-01.1 | Code follows industry best practices (SOLID, language linting rules). | SRS | Must | M0 | • ruff (lint + format), mypy + django-stubs, djLint; HackSoft-style services/selectors; import-linter module boundaries; all enforced in CI. |
| NFR-CODE-01.2 | Every change is peer reviewed before merge. | SRS | Must | M0 | • Branch protection: ≥ 1 approving review (2 for `credits`, `payments`, `leads`, security settings via CODEOWNERS); CI green required. |
| NFR-CODE-01.3 | Test coverage of at least 90 % (unit + integration). | SRS | Must | M0 | • CI gate: ≥ 90 % line+branch on domain code (models, services, selectors, gateways, tasks); ≥ 85 % on the whole repo excluding migrations, settings and generated files (GAP-15, OQ-30). |
| NFR-CODE-01.4 | Decisions and onboarding are documented. | Derived | Should | M0 | • ADRs for every architectural decision and SRS deviation; README/onboarding gets a new developer running locally in < 1 h. |

### NFR-OBS-01 — Observability (Derived)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| NFR-OBS-01.1 | Structured JSON logs with request and trace correlation. | Derived | Must | M0 | • structlog fields include `request_id`, `trace_id`, `user_public_id`, `release`. |
| NFR-OBS-01.2 | Errors, traces and metrics are collected. | Derived | Must | M0 | • Sentry; OpenTelemetry for Django, DB, Celery, Redis; business metrics (reveals, fulfilment latency, outbox age, ledger mismatches). |
| NFR-OBS-01.3 | Health and readiness endpoints. | Derived | Must | M0 | • `/healthz` (liveness), `/readyz` (DB, cache, broker). |
| NFR-OBS-01.4 | SLOs, dashboards and alerts route to on-call. | Derived | Must | M7 | • Alerts for SLO burn, ledger mismatch, webhook failures, outbox age, queue depth. |

### NFR-UX-01 — Credit visibility (SRS §11.1)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| NFR-UX-01.1 | The current credit balance is displayed prominently and persistently in the header, next to the profile icon, on every page for logged-in users. | SRS | Must | M4 | • Visible at 320 px width too; accessible name "Credit balance: {n} credits". |
| NFR-UX-01.2 | The balance stays current without a full reload. | Derived | Must | M4 | • Out-of-band HTMX update after reveal/purchase; polling every 30 s while the tab is visible. |

### NFR-UX-02 — Transaction confirmation (SRS §11.1)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| NFR-UX-02.1 | After a paid reveal, a minimal, non-modal confirmation shows: **"Contact revealed. 2 credits deducted. Details emailed to you."** | SRS | Must | M4 | • Exact copy (translated per locale); toast, not a modal; `role="status"`. |
| NFR-UX-02.2 | Free re-views and held emails get accurate copy instead. | Derived (GAP-37) | Must | M4 | • Re-view: no toast or "Contact shown. No credits used."; unverified email: "…Verify your email to receive the details." |

### NFR-UX-03 — Lister tag clarity (SRS §11.1)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| NFR-UX-03.1 | AgentListed and OwnerListed are styled distinctly on property cards: different background colours and icons (briefcase for agent, house for owner). | SRS | Must | M2–M3 | • One shared badge component used on cards, detail page and dashboard. |
| NFR-UX-03.2 | The tag is never conveyed by colour alone. | Derived (SRS §12) | Must | M2 | • Text label always present; badge contrast ≥ 4.5:1; icons `aria-hidden`. |

### NFR-UX-04 — Fluid navigation (SRS §11.2)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| NFR-UX-04.1 | The Profile Icon Dropdown renders immediately on mouse click and touch on all device sizes. | SRS | Must | M1 | • Menu markup is in the page (no network round trip to open); opens < 100 ms after input on a mid-range phone. |
| NFR-UX-04.2 | Opening the dropdown causes no layout shift. | SRS | Must | M1 | • Overlay positioning; CLS contribution 0. |
| NFR-UX-04.3 | The dropdown follows established menu conventions and is keyboard-operable. | SRS | Must | M1 | • Disclosure pattern; Escape closes and returns focus; Tab order logical. |

### NFR-UX-05 — Guided listing (SRS §11.2)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| NFR-UX-05.1 | The submission form shows a clear progress indicator (multi-step timeline). | SRS | Should | M2 | • `<nav><ol>` with `aria-current="step"` and text state per step. |
| NFR-UX-05.2 | Helpful inline validation messages guide the lister. | SRS | Should | M2 | • Message per rule (listings design §4.3) linked via `aria-describedby`. |
| NFR-UX-05.3 | Complex data entry is split into small sections. | SRS | Should | M2 | • ≤ 6 primary fields per step (photos excepted). |

### NFR-UX-06 — Mobile-first design (SRS §11.2)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| NFR-UX-06.1 | All UI components are designed for mobile first, especially the credit purchase workflow, property cards and search filters. | SRS | Must | M0+ | • Each component spec and review starts at 360 px; usable at 320 px with no horizontal scroll. |
| NFR-UX-06.2 | Touch targets are adequately sized. | SRS | Must | M0+ | • ≥ 44×44 CSS px for primary controls (never below 24×24). |
| NFR-UX-06.3 | Mobile performance meets the Core Web Vitals budgets (NFR-PERF-01.6). | SRS | Must | M0+ | • Lighthouse CI mobile budgets in CI. |

### NFR-UX-07 — Internationalisation readiness (Derived from SRS §1 "multinational")

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| NFR-UX-07.1 | All user-facing strings are translatable and locale-aware formatting is used for numbers, currency and dates. | Derived (GAP-52) | Must | M0 | • `makemessages` runs in CI; no hard-coded strings in templates (lint). English only at launch (OQ-31). |
| NFR-UX-07.2 | Times are stored in UTC and shown in the user's timezone. | Derived | Must | M0 | • `USE_TZ=True`; timezone on profile with browser default. |

### NFR-A11Y-01 — Accessibility (SRS §12)

| ID | Requirement | Src | Pri | MS | Acceptance criteria |
|---|---|---|---|---|---|
| NFR-A11Y-01.1 | The application conforms to WCAG 2.1 Level AA. | SRS | Must | Every story; audited M7 | • Manual audit of every page in the page inventory (NVDA+Firefox, VoiceOver macOS/iOS, TalkBack); no open AA failures at launch. |
| NFR-A11Y-01.2 | Full keyboard navigation. | SRS | Must | Every story | • Every interactive element reachable and operable by keyboard; visible focus; skip link; no keyboard traps (incl. dialogs, crop tool, filters sheet). |
| NFR-A11Y-01.3 | Adequate colour contrast across all elements. | SRS | Must | Every story | • Text ≥ 4.5:1 (large ≥ 3:1); UI components and focus indicators ≥ 3:1; design tokens checked in CI. |
| NFR-A11Y-01.4 | Proper semantic HTML and ARIA for screen readers. | SRS | Must | Every story | • Native elements first, ARIA only where needed; landmarks; labelled form controls; live regions for toasts and HTMX updates. |
| NFR-A11Y-01.5 | Automated accessibility checks run in CI. | Derived | Must | M0 | • axe-core in Playwright on key pages: 0 serious/critical violations. |

---

## 9. SRS coverage matrix

Every SRS clause maps to at least one requirement. Rationale-only phrases (e.g. "to improve conversion rates") are context and are not separate requirements.

| SRS § | Clauses → requirement IDs |
|---|---|
| 1.0 Introduction | credit-based model → FR-CRED-*, FR-PAY-*; scalable, multinational traffic, high volumes from launch → NFR-SCAL-01.2/01.3, NFR-PERF-02, NFR-UX-07; MVP single source of truth → this catalog + [01 §1.1](01-source-documents.md#11-precedence-rule) |
| 2.0 TOC | numbering defects → GAP-03 |
| 3.0 preamble | rigid authorization / RBAC (HLRD) → FR-AUTH-06.1–06.5 |
| 3.1 Sign-up | email/password → 01.1; format → 01.2; strength + complexity → 01.3; uniqueness real-time → 01.4; SSO Google/Apple (optional) → FR-AUTH-02.1–02.3 |
| 3.2 Verification | email confirmation → 03.2; phone OTP → 03.3; 'unverified' state → 03.1; restricted from listing/consuming credits → 03.4; protects promo credits → 03.5, FR-AUTH-04.4 |
| 3.3 Initial credits | first login, 10 credits, automatic → 04.1; one-time → 04.2; logged with date/source/quantity/user → 04.3 |
| 3.4 Login | verified credentials → 05.1; social sign-on → 05.2; hashing (bcrypt e.g.) → 05.3; "JWT for session management" → 05.4 (deviation); forgot password, time-limited link → 05.5 |
| 4.1 Submission | logged-in users → FR-LIST-01.1; multi-step → 01.2; draft → 01.3; client-side validation → 01.4 |
| 4.2 Required fields | address → 02.1; type → 02.2; price → 02.3; description → 02.4; images 3–20 → 02.6; contact phone/email → 02.7; formats → 02.10; aspect ratio → 02.12; 5 MB → 02.11; thumbnails for all devices → 02.13 |
| 4.3 Lister tag | required, exclusive two values → 03.1; renter trust, filtering, analytics → 03.2, FR-LIST-05.6, NFR-UX-03; no modification without admin review → 03.3, 03.4 |
| 4.4 Listing management | view → 04.1; edit → 04.2; mark as rented → 04.3; unlist → 04.4; status controls → 04.5; quick edit links → 04.2; metrics views/saves/Show Number clicks → 04.7–04.9; "instantly" → 04.10 |
| 4.5 Search & filter | visitors → 05.1; location → 05.3; price range → 05.4; type → 05.5; tag → 05.6; geospatial → 05.3; multi-select → 05.5–05.7; sort newest/price → 05.8; fuzzy → 05.9; fast and relevant index → 05.10, NFR-PERF-01.1/01.2 |
| 5.1 Button visibility | "Show Number" label → FR-CRED-01.1; logged-in and balance > 0 → 01.2; 2-credit cost adjacent → 01.3 |
| 5.2 Credit check | ≥ 2 → 02.1; atomic with deduction → 02.2; no negative balance → 02.3; no unauthorised deduction → 02.4 |
| 5.3 Deduction | deduct 2 immediately → 03.1; immutable ledger with transaction ID, balance before/after, timestamp, property ID, server process ID → 03.2, 03.3, NFR-SEC-02 |
| 5.4 Contact display | phone and/or email after deduction, modal/designated area → 04.1; accessible in transaction history without cost → 04.2 |
| 5.5 Email | triggered with deduction → 05.1, 05.3; link, lister name, title, full description, confirmation → 05.2; receipt and lead record → 05.2; reliable monitored service → 05.4 |
| 5.6 Insufficient credit | < 2 → non-disruptive toast/alert → 06.1; concise, states required amount → 06.2; high-contrast link to Purchase Credits → 06.3 |
| 6.1 Purchase access | schema integrity and speed → FR-PAY-01.4; Users `last_login_date`, `mfa_enabled` → 01.5; Menu_Items `allergy_flags` → 01.6 (Won't); Purchase Credits tab → 01.1; minimal steps desktop/mobile → 01.2; seamless responsive funnel → 01.3 |
| 6.2 Packages | multiple distinct packages (20/50/120 e.g.) → 02.1; pricing → 02.2; volume discounts → 02.3; localised currency by IP or account region → 02.4, 02.5 |
| 6.3 Payment integration | ≥ 2 global gateways → 03.1; card/digital wallet → 03.2; tokenisation → 03.3, NFR-SEC-03; webhooks for fulfilment, status, errors → 03.4, 03.6 |
| 6.4 Instant allocation | within 5 s → 04.1; verified via gateway webhook before applying → 04.2; visible balance updated → 04.4 |
| 6.5 Transaction history | all purchases and consumption → 05.1; date, time, amount, label → 05.2; distinguish purchases with payment method → 05.3; property ID for consumption → 05.4; filterable → 05.5 |
| 7.0 Profile icon | avatar/silhouette top-right → FR-PROF-01.1 |
| 7.1 Dropdown access | click reveals persistent dropdown → 01.2, 01.5; balance below name/email at top → 01.3; central hub → 01.4 |
| 7.2 Dropdown tabs | at least three tabs → 02.1; Profile fields → 02.2; validation → 02.3; two-step email/password → 02.4, 02.5; preferences → 02.7; My Properties dashboard → 02.8; quick statistics views/reveals/performance → 02.9; Purchase Credits workflow → 02.10; packages, pricing, discounts, secure payment → 02.11 |
| 7.3 Logout | bottom of dropdown → 03.1; terminate server session → 03.2; invalidate all tokens → 03.3; clear local artefacts → 03.4 |
| 8.1 Latency | search 500/1000 ms → NFR-PERF-01.1/01.2; credit transactions 500/1000 ms → 01.3/01.4; indexing, read replicas, CDN → 01.5 |
| 8.2 Concurrency | 1,000 TPS deduction without inconsistency or degradation → NFR-PERF-02.1–02.3; isolation/locking/queue mechanism → 02.4 |
| 8.3 Availability | restore testing → NFR-AVAIL-01.2; runbooks incl. payment API failure and DB degradation → 01.3; (no targets in SRS → 01.4–01.6 proposed) |
| 9.1 Encryption | in transit TLS 1.2+ → NFR-SEC-01.1; at rest AES-256 → 01.2; passwords, payment info, contact numbers, PII → 01.3, 01.6, 01.4; tokenise/pseudonymise PII → 01.5 |
| 9.2 Credit integrity | secure storage, no manipulation → NFR-SEC-02.1; ledger service or cryptographically linked trail → 02.2, 02.3; regular audits → 02.4; automated alerts → 02.5 |
| 9.3 Payment compliance | PCI DSS via certified gateways → NFR-SEC-03.1; tokenisation, no raw card data → 03.2 |
| 10.1 Cloud native | cloud-native services → NFR-SCAL-01.1; horizontal scale across global markets → 01.2, 01.3; IaC (Terraform/CloudFormation) → 01.4; rapid consistent deployment → 01.5 |
| 10.2 Code standards | SOLID and linting → NFR-CODE-01.1; mandatory peer review → 01.2; ≥ 90 % unit+integration coverage → 01.3 |
| 11.1 Transparency | credit visibility in header → NFR-UX-01; confirmation toast copy → NFR-UX-02; tag styling on cards → NFR-UX-03 |
| 11.2 Interaction | fluid dropdown, click and touch, no layout shift → NFR-UX-04; guided listing → NFR-UX-05; mobile-first (purchase, cards, filters), touch targets, performance → NFR-UX-06 |
| 12.0 Accessibility | WCAG 2.1 AA → NFR-A11Y-01.1; keyboard → 01.2; contrast → 01.3; semantic HTML/ARIA → 01.4 |

### 9.1 Diagram coverage (SRC-03 / SRC-04)

| Diagram element | Requirement IDs | MVP? |
|---|---|---|
| Renter portal: search & details | FR-LIST-05, FR-CRED | Yes |
| Renter portal: lead forms; "Submit inquiry"; "LEAD created"; "Lister notified of new lead" | FR-LEAD-01.1, FR-LEAD-01.2 | Post-MVP (OQ-01, OQ-21, OQ-17) |
| Lister portal: post & manage listings | FR-LIST-01…04 | Yes |
| Lister portal: credit wallet; "Credit wallet setup" | FR-CRED-07.1, FR-PAY-05 | Yes (no setup step, GAP-53) |
| "Lister wants to unlock lead?" → "Atomic credit debit" → "Lead unlocked — contact revealed" | FR-LEAD-01.3 (lister-pays); MVP equivalent is the renter reveal FR-CRED-02/03 | Post-MVP for lister-pays |
| "Select credit pack & pay" → "Payment successful?" (retry) | FR-PAY-02, FR-PAY-03.6, FR-PAY-04 | Yes |
| "Mark listing as rented / delist" | FR-LIST-04.3, FR-LIST-04.4 | Yes |
| Ops console: monitor & manage jobs, listing moderation, fraud review | FR-OPS-01…07 | Yes (M6) |
| Verification API; KYC docs; ownership proofs | FR-KYC-01 | Post-MVP (hooks in MVP) |
| Maps & geocoding (address geocoding, map tiles) | FR-LIST-02.1, FR-LIST-05.3; map tiles OQ-27 | Geocoding yes |
| Notification services: OTP delivery, Twilio, Mailgun | FR-AUTH-03.3, FR-NOTIF-01 | Yes |
| Cache: hot search results, session store, polled HTTP | NFR-PERF-01.5, FR-AUTH-05.4, NFR-UX-01.2, FR-LIST-04.10 | Yes |
