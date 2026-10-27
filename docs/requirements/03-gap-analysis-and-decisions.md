# Gap Analysis and Decisions

Purpose: every contradiction, error, vague or infeasible statement and silent area found in the source documents, each with the SRS text, the problem, its impact, the adjustment we propose and its status. Every **Deviation from SRS** in the knowledge base traces back to an entry here.

Status: Draft v0.1 (2026-10-21)

Related: [01 Source Documents](01-source-documents.md) · [02 Requirements Catalog](02-requirements-catalog.md) · [04 Open Questions](04-open-questions.md) · [05 Glossary](05-glossary.md) · [Development Approach §7](../delivery/01-development-approach.md)

---

## 0. How to read this document

| Item | Rule |
|---|---|
| **IDs** | `GAP-nn`, stable and never reused. **GAP-01 … GAP-22 correspond one-to-one to known issues #1 … #22** in the team brief. GAP-23 onwards were found during the requirements analysis. |
| **Type** | `CONTRA` sources contradict each other or themselves · `DEFECT` editorial error in a source · `VAGUE` ambiguous or not measurable · `INFEAS` infeasible, unsafe or self-defeating as written · `MISSING` the SRS is silent on something the product needs · `DIAGRAM` appears only in the AI-generated diagrams |
| **Severity** | **High**: touches a CRITICAL requirement, money, security/privacy or a milestone's architecture · **Medium**: changes feature behaviour, UX or milestone scope · **Low**: editorial or local |
| **Status** | Every entry is **Proposed — awaiting stakeholder confirmation** until signed off. Answers are recorded in the [decision log](04-open-questions.md#5-decision-log), and the entry then changes to *Accepted*, *Rejected* or *Superseded* with a date. |
| **Markers** | **Deviation from SRS:** we knowingly do something other than the SRS text. **Assumption:** we fill a silence with a default. **Proposed change:** another writer proposes to change a team baseline; the baseline stays in force until the linked question is answered. |
| **Citations** | SRS sections use the TOC numbering (GAP-03). `SRC-03` / `SRC-04` are the diagrams ([01 §1](01-source-documents.md#1-inventory)). |

---

## 1. Summary index

| GAP | Title | Type | Sev | SRS § | Decision (short) | Deviation? | OQ |
|---|---|---|---|---|---|---|---|
| [01](#gap-01) | Monetisation model: renter pays vs lister pays | CONTRA | High | 1.0, 5.x, SRC-03 | Renter-pays "Show Number" for MVP; generic ledger; lister-pays and inquiry forms Post-MVP | No (SRS kept) | OQ-01, OQ-21 |
| [02](#gap-02) | Copy-paste and text defects | DEFECT | Low | cover, 1.0, 5.1, 6.1, HLRD | Drop `Menu_Items`; keep last-login and `mfa_enabled`; SRS wins over HLRD | Naming only | — |
| [03](#gap-03) | Broken cross-references and TOC pages | DEFECT | Low | 2.0, body | Cite TOC numbers; old `2.N.M` = `(N+2).M` | No | — |
| [04](#gap-04) | "Three core user types" undefined | VAGUE | Medium | HLRD 3.0 | Renter + Lister (capabilities of one account), Staff with four sub-roles | No | OQ-02 |
| [05](#gap-05) | Show Number visibility vs insufficient credit vs anonymous | CONTRA | High | 5.1, 5.2, 5.6 | Explicit viewer-state table; one charge per (user, property) | No | OQ-44 |
| [06](#gap-06) | Promo credits on "first login" vs unverified restriction | CONTRA | High | 3.2, 3.3 | Grant once when the account first becomes verified; one per verified identity | **Yes** | OQ-11 |
| [07](#gap-07) | JWT for browser sessions | INFEAS | High | 3.4, 7.3 | Server-side sessions; Argon2id; JWT only for a future API | **Yes** | — |
| [08](#gap-08) | Prescribed concurrency mechanisms | INFEAS | High | 8.2 | PostgreSQL READ COMMITTED + row lock / conditional UPDATE + constraints; no Kafka | **Yes** | OQ-09 |
| [09](#gap-09) | Webhook-only allocation within 5 s | INFEAS | High | 6.3, 6.4 | Webhook **or** server-side gateway verification; exactly-once; reconciliation | **Yes** | — |
| [10](#gap-10) | Email "concurrently" with the deduction | INFEAS | High | 5.5 | Transactional outbox, sent after commit | **Yes** | — |
| [11](#gap-11) | "Cryptographically-linked audit trail" | VAGUE | High | 9.2 | Per-wallet SHA-256 hash chain, append-only triggers, nightly audit, WORM anchor | No | — |
| [12](#gap-12) | AES-256 at rest and PII tokenisation | VAGUE | High | 9.1 | KMS storage encryption + field-level AES-256-GCM + HMAC blind indexes | Proposed change (login email) | OQ-29 |
| [13](#gap-13) | Localised currency "by IP or account region" | VAGUE | Medium | 6.2 | Per-currency price book; account region → GeoIP → market default | Interpretation | OQ-03, OQ-04 |
| [14](#gap-14) | "At least two" payment gateways | VAGUE | Medium | 6.3 | `PaymentGateway` adapter; Stripe Checkout + PayPal Orders v2; Razorpay optional | No | OQ-07 |
| [15](#gap-15) | 90 % coverage, scope undefined | VAGUE | Low | 10.2 | ≥ 90 % domain code; ≥ 85 % repo, ratcheting | Partial | OQ-30 |
| [16](#gap-16) | Availability section without targets | MISSING | Medium | 8.3 | Propose 99.9 % / RPO ≤ 5 min / RTO ≤ 1 h | Addition | OQ-08 |
| [17](#gap-17) | Latency targets not measurable as written | VAGUE | High | 8.1 | Server-side p95; PostGIS + trigram + FTS, cache, replica, CDN | **Yes** | OQ-09 |
| [18](#gap-18) | Capabilities only in the diagrams | DIAGRAM | Medium | SRC-03 | Ops console in MVP; KYC, lead forms, lead alerts Post-MVP | Addition | OQ-17, OQ-20, OQ-21 |
| [19](#gap-19) | "Saves" metric without a save feature | MISSING | Low | 4.4 | Saved properties in M3 | Addition | OQ-42 |
| [20](#gap-20) | Listing contact information | VAGUE | High | 4.2, 5.4 | Listing-level, encrypted, never in any response before reveal | No | OQ-37 |
| [21](#gap-21) | Image rules without values | VAGUE | Medium | 4.2 | Presigned S3 upload, async sanitising pipeline, explicit ratio policy | No | OQ-23 |
| [22](#gap-22) | Tag "administrative review" undefined | VAGUE | Medium | 4.3 | `PropertyTagChangeRequest` reviewed by a Moderator | No | OQ-18, OQ-36 |
| [23](#gap-23) | SSO "(optional)" vs "must" | CONTRA | Low | 3.1 | Could; M1 stretch, else Post-MVP | No | OQ-14 |
| [24](#gap-24) | Social account linking and verification | MISSING | Medium | 3.1 | Link only on provider-verified email | Addition | OQ-14 |
| [25](#gap-25) | "Recommendations" section with MUST statements | DEFECT | Low | 11.0 | Modality decided per sentence | No | — |
| [26](#gap-26) | Email **or** phone verification | VAGUE | Medium | 3.2, 5.5 | Either activates; reveal email held until email verified | No | OQ-10 |
| [27](#gap-27) | "Complexity rules" unspecified | VAGUE | Low | 3.1 | Length + blocklist + similarity; no composition rules | Assumption | OQ-15 |
| [28](#gap-28) | Real-time email uniqueness enables enumeration | INFEAS | Medium | 3.1 | Keep, with rate limits and a challenge | No | OQ-15 |
| [29](#gap-29) | "Transactional activities" undefined | VAGUE | Medium | 3.2 | Explicit restricted-action list | No | OQ-10 |
| [30](#gap-30) | Login before verification | CONTRA | Medium | 3.3, 3.4 | Unverified users may log in, restricted | No | OQ-10 |
| [31](#gap-31) | Refunds and chargebacks | MISSING | High | — | `REVERSAL` entries, never negative, Finance-only refunds | Addition | OQ-05 |
| [32](#gap-32) | Credit expiry | MISSING | Medium | — | Credits never expire in MVP | Assumption | OQ-12 |
| [33](#gap-33) | "Server process ID" | VAGUE | Low | 5.3 | `service:task:pid` + request ID + release | No | — |
| [34](#gap-34) | Revealed contact "without further cost" over time | VAGUE | Medium | 5.4 | Encrypted snapshot (24 months) plus current contact | No | OQ-13 |
| [35](#gap-35) | Show Number on "all property listings" | VAGUE | Low | 5.1 | Detail page only; cards link to it | Interpretation | OQ-44 |
| [36](#gap-36) | Reveal email omits the contact itself | MISSING | Medium | 5.5 | Include the revealed contact | Addition | OQ-34 |
| [37](#gap-37) | Fixed toast copy is sometimes false | CONTRA | Low | 11.1 | Variant copy for free re-views and held emails | No | — |
| [38](#gap-38) | Reveal on rented / unlisted listings | VAGUE | Medium | 5.1 | Only `PUBLISHED` listings offer Show Number | Interpretation | — |
| [39](#gap-39) | Metrics "instantly" | INFEAS | Low | 4.4 | ≤ 60 s counters; saves and reveals immediate | **Yes** | OQ-38 |
| [40](#gap-40) | Metric definitions | VAGUE | Low | 4.4, 7.2 | Views, saves, clicks, reveals defined | No | — |
| [41](#gap-41) | "Location" search semantics | VAGUE | Medium | 4.5 | City match or radius; one market per search | No | OQ-27, OQ-33 |
| [42](#gap-42) | Price filter across currencies and periods | VAGUE | Low | 4.5 | Monthly equivalent in market currency; no FX | No | OQ-33 |
| [43](#gap-43) | Minimal listing attributes, no type list | MISSING | Medium | 4.2 | Title mandatory; optional attributes; type enum | Addition | OQ-24 |
| [44](#gap-44) | Client-side validation and drafts | VAGUE | Low | 4.1 | Server authoritative; lenient drafts | No | — |
| [45](#gap-45) | Listing expiry and draft retention | MISSING | Medium | 4.4 | 60-day expiry with renewal; 90-day draft archive | Addition | OQ-26 |
| [46](#gap-46) | Listing moderation policy | MISSING | Medium | SRC-03 | Post-publish with risk-based pre-moderation | Addition | OQ-19, OQ-40 |
| [47](#gap-47) | "Persistent" dropdown | VAGUE | Low | 7.1 | Stays open until dismissed; on every page | No | — |
| [48](#gap-48) | "Secure two-step processes" | VAGUE | Medium | 7.2 | Re-auth + confirm new value + notify old | No | — |
| [49](#gap-49) | Logout "all active session tokens" | VAGUE | Medium | 7.3 | Current session + "sign out of all devices" | No | — |
| [50](#gap-50) | Password listed as a viewable detail | DEFECT | Low | 7.2 | Change-only | No | — |
| [51](#gap-51) | Privacy and data protection | MISSING | High | — | Privacy-by-design baseline | Addition | OQ-28 |
| [52](#gap-52) | "Multinational" without languages or locales | MISSING | Medium | 1.0 | i18n-ready code, English at launch | Assumption | OQ-31 |
| [53](#gap-53) | "Credit wallet setup" step | DIAGRAM | Low | SRC-03 | Wallet automatic for every user | No | — |
| [54](#gap-54) | NGINX/WhiteNoise box and polling placement | DIAGRAM | Low | SRC-03 | CloudFront + WhiteNoise; S3 media; browser polling | No | — |
| [55](#gap-55) | Purchase latency includes gateway time | INFEAS | Medium | 8.1 | Measure our side only | **Yes** | — |
| [56](#gap-56) | "1,000 concurrent transactions per second" | VAGUE | High | 1.0, 8.2 | Sustained 1,000 debits/s design ceiling; email backlog via outbox | Interpretation | OQ-09 |
| [57](#gap-57) | Tax on credit purchases | MISSING | High | — | Tax-inclusive price book pending Finance | Assumption | OQ-06 |
| [58](#gap-58) | Launch markets, region, data residency | MISSING | High | 1.0, 10.1 | Single parameterised AWS region | Assumption | OQ-33 |
| [59](#gap-59) | "Lister notified of new lead" | DIAGRAM | Medium | SRC-03 | No per-reveal lister notification in MVP | No | OQ-17 |
| [60](#gap-60) | Account closure and unused credits | MISSING | Medium | — | Support-led erasure; anonymise; 7-day unverified purge | Assumption | OQ-16 |
| [61](#gap-61) | Public visibility of the exact address | MISSING | Medium | 4.2 | `APPROXIMATE` by default | Addition | OQ-22 |
| [62](#gap-62) | Staff MFA (`mfa_enabled`) | MISSING | High | 6.1 (stray) | MFA mandatory for staff | Addition | OQ-41 |
| [63](#gap-63) | Ownership of the listing contact phone | MISSING | Medium | 4.2 | OTP when it differs from the account phone | Addition | OQ-25 |
| [64](#gap-64) | Hard-coded business constants | VAGUE | Low | 3.3, 5.x, 6.2 | Configurable, applied prospectively | No | OQ-43 |
| [65](#gap-65) | Contact details in free text or photos | MISSING | High | — | Block clear matches; flag obfuscated ones | Addition | OQ-39 |
| [66](#gap-66) | Reveal abuse and contact scraping | MISSING | High | — | Rate limits, velocity flags, wallet freeze | Addition | OQ-35 |
| [67](#gap-67) | Transaction history scope and filters | VAGUE | Low | 6.5 | All entry types; type and date filters | No | — |
| [68](#gap-68) | Toast notifications vs WCAG | CONTRA | Medium | 5.6, 11.1, 12.0 | Accessible live-region toasts | No | — |
| [69](#gap-69) | Modal vs non-modal reveal presentation | CONTRA | Low | 5.4, 11.1 | Inline contact area + toast; no modal | No | — |

Totals: 69 entries: 19 High, 29 Medium, 21 Low. The [deviation register](#3-deviation-register) lists 10 deviations from the SRS, 4 documented interpretations and 1 proposed change to a team baseline.

---

## 2. Entries

<a id="gap-01"></a>
### GAP-01 — Monetisation model: renter pays (SRS) vs lister pays (flow chart)

- **Type / severity:** CONTRA · High
- **SRS text:** §1.0 "The platform will operate on a credit-based consumption model to monetize lead generation." §5.1 "the primary call-to-action button for accessing the lister's contact information shall be labeled 'Show Number' … display the 2-credit cost." §5.3 "deduct 2 credits from the user's account."
- **Diagram text (SRC-03):** Renter: "Submit inquiry / contact request" → "LEAD created" → "Lister notified of new lead". Lister: "Lister wants to unlock lead?" → "Select credit pack & pay" → "Atomic credit debit" → "Lead unlocked — contact revealed" → "Lister contacts renter". Architecture: "Renter / Seeker Portal (… lead forms)", "Lister / Owner Portal (… credit wallet)", "owner wallet dashboard".
- **Problem:** two incompatible business models.

  | Aspect | SRS (renter pays) | Flow chart (lister pays) |
  |---|---|---|
  | Who pays | Renter | Lister |
  | What is sold | Lister's phone/email | Renter's inquiry and contact |
  | What a "lead" is | A paid contact reveal | A free inquiry from a renter |
  | Renter data shared with lister | None | Name, contact, message |

- **Impact:** decides the whole of M4 (flows, UX, privacy notices, pricing, analytics). It is the highest-impact ambiguity in the sources.
- **Decision:**
  1. The **SRS is authoritative for MVP**: renter pays 2 credits to "Show Number". Reasons: the SRS is later (Oct 2025 vs Aug 2025 file dates), it calls itself the "single source of truth for the MVP", and all of its CRITICAL items (§5.1–5.3) describe renter-pays.
  2. In MVP a **lead is a `leads.ContactReveal`** (one paid reveal by one user of one property).
  3. The credit design is **model-agnostic**: every user has one wallet regardless of role; debits go through `credits.services.debit_credits(wallet, amount, entry_type, reference, idempotency_key, reason_code)`. A lister-pays model is added later as a new entry type (`LEAD_UNLOCK`, reserved) and a new caller, with no schema change to wallets or the ledger (FR-CRED-07.4).
  4. Free inquiry forms, lead records owned by listers, lister lead alerts and lister-pays unlock are **Post-MVP** (FR-LEAD-01).
- **Structural risk to flag to stakeholders:** under renter-pays, listers gain nothing from the paywall and may try to publish their number in free text or photos. GAP-65 is therefore a revenue control, not only a quality rule.
- **Affects:** FR-CRED-01 … 08, FR-CRED-07.4, FR-LEAD-01, FR-PROF-02.9, FR-LIST-04.9.
- **Status:** Proposed — awaiting stakeholder confirmation. **Blocking for M4** (OQ-01; free inquiry OQ-21; lister notifications OQ-17).

<a id="gap-02"></a>
### GAP-02 — Copy-paste and text defects

- **Type / severity:** DEFECT · Low
- **SRS text:**
  - Cover, twice (also the `.docx` subject property): "Project: Restaurant Online Web Application".
  - §6.1 Purchase Access: "The database schema must be designed for transactional integrity and speed. The Users table should include fields for last_login_date and mfa_enabled status. The Menu_Items table must include essential dimensions for allergy_flags (stored as a JSON array of strings) and The option to purchase additional credits shall be prominently accessible …", followed by a stray "." paragraph.
  - §1.0 "This The goal of this project …". §5.1 starts mid-sentence: "all property listings, the primary call-to-action …".
  - HLRD: §5.2 "verify balance 2 credits" and §5.6 "If balance 2 credits" (comparison operators missing in the source), §8.1 "read-replicas for static assets", §1.0 words missing ("scalable marketplace and high transaction volumes").
- **Problem:** text from another project's template, plus garbled sentences.
- **Impact:** low if ignored, but someone could build a `Menu_Items` table or read the HLRD operators wrongly. It also weakens the SRS as a contractual baseline.
- **Decision:**
  - The project is the "Rent Property Listing Web Application".
  - `Menu_Items` / `allergy_flags` are dropped (FR-PAY-01.6, *Won't*).
  - The Users fields are kept as intent: last login time uses Django's built-in `User.last_login`; `mfa_enabled` is derived from allauth MFA authenticators (FR-PAY-01.5). **Deviation from SRS (naming only):** no separate `last_login_date` column.
  - "Schema designed for transactional integrity and speed" is kept as FR-PAY-01.4 (constraints, idempotency keys, indexes on hot paths).
  - Where the HLRD is garbled, the SRS wins (≥ 2 credits to reveal, < 2 is insufficient).
  - Ask the client to publish SRS v1.1 with these fixes.
- **Status:** Proposed — awaiting stakeholder confirmation (editorial).

<a id="gap-03"></a>
### GAP-03 — Broken cross-references and wrong TOC page numbers

- **Type / severity:** DEFECT · Low
- **SRS text:** body references "2.5.2.2", "2.2.4", "2.4.1", "2.3.3", "2.2.1", "2.5"; the TOC numbers sections 1.0–12.0; body headings are unnumbered bullets; TOC lists §8.1 and §8.2 on page 6 while §8.0 is on page 7.
- **Problem:** the body uses an older numbering scheme, so no reference resolves.
- **Decision:** all documents cite the **TOC numbers**. Old `2.N.M` maps to TOC `(N+2).M`. Full table in [01 §2.1](01-source-documents.md#21-broken-internal-cross-references).
- **Status:** Proposed — awaiting stakeholder confirmation (editorial).

<a id="gap-04"></a>
### GAP-04 — "Three core user types" are never defined

- **Type / severity:** VAGUE · Medium
- **SRS text:** §3.0 "The system implements a rigid authorization for users." HLRD §3.0 "a rigid Role-Based Access Control (RBAC) model to enforce authorization for three core user types." SRC-03: "User Role Choice?" splitting renter and lister journeys.
- **Problem:** the types are never named. The flow chart implies choosing a role, while SRS §7.2 gives every user both "My Properties" and "Purchase Credits", which implies one account type that can do both.
- **Impact:** sign-up UX, authorisation model, permission tests, analytics.
- **Decision:** the three types are **Renter**, **Lister** and **Staff**.
  - Renter and Lister are **capabilities of any verified account**, not exclusive roles. There is no role choice at sign-up. Owner vs Agent is a per-listing tag (FR-LIST-03), not an account type.
  - Staff sub-roles are Django groups with fixed permission sets: **Moderator**, **Support**, **Finance**, **Superadmin**. Staff need MFA (GAP-62).
  - Anonymous visitors are not a user type but have explicit rights (browse and search).
  - **Assumption:** staff use dedicated staff accounts and do not rent or list from them, which keeps the audit trail unambiguous.

  | Capability | Anonymous | Unverified | Verified user | Moderator | Support | Finance | Superadmin |
  |---|---|---|---|---|---|---|---|
  | Search, view listings | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
  | Create/publish listings, Show Number, buy credits, save | — | — | ✓ | — | — | — | — |
  | Request a tag change (own listing) | — | — | ✓ | — | — | — | — |
  | Moderation queue, tag-change decisions | — | — | — | ✓ | — | — | ✓ |
  | User lookup (PII masked; unmask with reason) | — | — | — | — | ✓ | — | ✓ |
  | Request credit adjustment (maker) | — | — | — | — | ✓ | ✓ | — |
  | Approve credit adjustment (checker, different person) | — | — | — | — | — | ✓ | — |
  | Ledger audit dashboard, payment re-verification | — | — | — | — | re-verify only | ✓ | ✓ |
  | Jobs monitor, outbox retry, group management | — | — | — | — | — | — | ✓ |

- **Affects:** FR-AUTH-06.1 … 06.5, FR-OPS-*.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-02).

<a id="gap-05"></a>
### GAP-05 — Show Number visibility vs insufficient-credit toast vs anonymous users

- **Type / severity:** CONTRA · High
- **SRS text:** §5.1 "This button must only be visible to logged-in users who possess a positive credit balance (Credit Count > 0)". §5.2 "verify if the user's current credit balance is greater than or equal to 2 credits". §5.6 "If the user has fewer than 2 credits, the system shall display a non-disruptive, in-app notification (e.g., a toast …)".
- **Problem:**
  1. With the "> 0" visibility rule, the "< 2" toast can only appear at balance 1 (or if the balance drops after the page loads).
  2. Anonymous and zero-balance users get no call to action at all: a dead end on the page that matters most for conversion.
  3. Own listings, already-revealed listings and repeated clicks are not covered.
- **Impact:** a CRITICAL requirement; directly affects revenue, double-charging risk and support load.
- **Decision:** the literal rule (button hidden unless balance > 0) is kept, and every other viewer state gets an explicit alternative:

  | Viewer state | What is rendered | On click |
  |---|---|---|
  | Anonymous | "Log in to view number" | Login, then back (`next`) |
  | Logged in, unverified | "Verify to view number" | Verification page |
  | Verified, balance 0 | "Get credits to view number" (Show Number hidden) | Purchase Credits |
  | Verified, balance 1 | "Show Number · 2 credits" | Insufficient-credit toast with "Buy credits" link; nothing deducted |
  | Verified, balance ≥ 2 | "Show Number · 2 credits" | Atomic debit, contact revealed |
  | Already revealed this property | Contact shown, "Revealed on {date}" | — (free, no second charge) |
  | Owner of the listing | Own contact shown, no button | — (service also rejects self-reveal) |
  | Listing not `PUBLISHED` | "No longer available" | — (GAP-38) |

  ```mermaid
  flowchart TD
      A[Listing detail page] --> B{Logged in?}
      B -- no --> L["Log in to view number"]
      B -- yes --> C{Owner?}
      C -- yes --> O[Own contact shown]
      C -- no --> D{Already revealed?}
      D -- yes --> R[Contact shown free]
      D -- no --> E{Verified?}
      E -- no --> V["Verify to view number"]
      E -- yes --> F{Balance > 0?}
      F -- no --> G["Get credits to view number"]
      F -- yes --> S["Show Number · 2 credits"]
      S --> H{"Atomic debit: balance >= 2?"}
      H -- no --> T[Insufficient-credit toast + Buy credits link]
      H -- yes --> X[Contact revealed + confirmation toast]
  ```

  Idempotency: `ContactReveal` has `UNIQUE (user, property)`; a double click, retry or second tab produces one debit and one reveal.
- **Affects:** FR-CRED-01.1 … 01.7, FR-CRED-02, FR-CRED-03.4, FR-CRED-06.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-44 asks whether hiding the button at balance 0 is really wanted).

<a id="gap-06"></a>
### GAP-06 — Promo credits on "first successful login after registration" vs unverified restriction

- **Type / severity:** CONTRA · High
- **SRS text:** §3.3 "Upon the first successful login after registration, the system MUST automatically allocate 10 complimentary credits … strictly logged internally with metadata (date, source 'promo', quantity, user ID)." §3.2 "The user's account state must remain 'unverified' and restricted from transactional activities … mitigating spam accounts and preventing unauthorized access and misuse of promotional credits."
- **Problem:**
  1. Unverified users may log in (GAP-30), and with allauth the sign-up itself usually logs the user in. The literal trigger would give credits to unverified accounts, which §3.2 forbids.
  2. Free credits are an incentive to farm accounts (each farmed account = 5 free reveals = contact scraping, GAP-66).
- **Impact:** CRITICAL requirement; revenue leakage; lister privacy.
- **Decision:**
  - Grant **exactly once, when the account first becomes verified**: at the first login after verification, or at the moment of verification if the user is already logged in. The grant runs in the same transaction that creates the wallet (GAP-53).
  - Idempotency and uniqueness at DB level: partial unique index "one `SIGNUP_PROMO` per wallet", idempotency key `promo:signup:<user_public_id>`, and `credits.SignupPromoClaim` with unique HMACs of the verified email and phone, so **one promo per verified identity**, even across deleted accounts.
  - Anti-abuse: disposable-email blocklist, per-IP/device sign-up rate limits, CAPTCHA (Cloudflare Turnstile) switchable by flag, fraud flags for promo-only accounts that reveal immediately (FR-OPS-04.1).
  - Logged metadata: ledger entry `SIGNUP_PROMO`, `amount = +10`, `created_at`, wallet/user, `reason_code = SIGNUP_10`, metadata `{"source": "promo"}`, included in the hash chain.
- **Deviation from SRS:** trigger moves from "first login after registration" to "first verified login (or verification)". The intent of §3.2 and §3.3 is met.
- **Affects:** FR-AUTH-03.5, FR-AUTH-04.1 … 04.5, FR-AUTH-01.5.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-11 on stronger anti-abuse).

<a id="gap-07"></a>
### GAP-07 — "JWT for session management" and "e.g. bcrypt"

- **Type / severity:** INFEAS · High
- **SRS text:** §3.4 "Secure authentication must utilize industry-standard hashing (e.g., bcrypt) and encryption protocols (e.g., JWT for session management)". §7.3 "The logout action must securely terminate the user's session on the server side, invalidate all active session tokens, and clear any associated local authentication artifacts."
- **Problem:**
  - JWT is a signed token format, not an encryption protocol.
  - A stateless JWT stays valid until it expires. Revoking it needs a server-side denylist, which is a session store by another name. This conflicts with §7.3.
  - In a server-rendered monolith, JWTs in browser storage are readable by any XSS; HttpOnly cookies are not.
- **Impact:** security of every authenticated request; M1 architecture.
- **Decision:**
  - Server-side Django sessions (`cached_db` backend on Valkey/Redis + PostgreSQL), cookie `__Host-` prefixed, `Secure`, `HttpOnly`, `SameSite=Lax`; session key rotated on login and privilege change; logout deletes the session (GAP-49). ADR-0003.
  - JWT (DRF + SimpleJWT, short-lived access tokens, rotating refresh tokens with blacklist) is reserved for the Post-MVP mobile/public API.
  - Hashing: **Argon2id** primary (Django's recommended hasher, preferred by OWASP), bcrypt (`BCryptSHA256PasswordHasher`) as fallback hasher. "e.g. bcrypt" makes this compliant.
- **Deviation from SRS:** no JWT for browser sessions. The SRS's own logout requirement is met better this way.
- **Affects:** FR-AUTH-05.3, FR-AUTH-05.4, FR-PROF-03.
- **Status:** Proposed — awaiting stakeholder confirmation.

<a id="gap-08"></a>
### GAP-08 — Prescribed concurrency mechanisms (serializable, optimistic locking, Kafka)

- **Type / severity:** INFEAS · High
- **SRS text:** §8.2 "The credit deduction mechanism (2.3.3) must be capable of handling 1,000 concurrent transactions per second without data inconsistency or degradation of service. This necessitates utilizing database transaction isolation levels (e.g., serializable), optimistic locking, or a resilient, queue-based processing system (like Apache Kafka) to prevent race conditions during credit updates."
- **Problem:** each listed mechanism has a cost the SRS does not acknowledge.
  - `SERIALIZABLE` aborts conflicting transactions with serialisation failures that must be retried; under load this adds latency and retry storms.
  - Optimistic locking (version column) also retries on every conflict, worst on a "hot" wallet.
  - Kafka makes the debit asynchronous, which contradicts §5.3 "immediately deduct" and §5.4 "immediately display", and adds a platform to operate.
- **Impact:** CRITICAL money path; M4 design; M7 load test.
- **Decision:** PostgreSQL short transactions at the default **READ COMMITTED** isolation level, with a row-level lock on the wallet row:

  ```sql
  -- inside transaction.atomic(); one wallet row, one statement
  UPDATE credits_creditwallet
     SET balance = balance - 2, updated_at = now()
   WHERE id = %(wallet_id)s AND status = 'ACTIVE' AND balance >= 2
  RETURNING balance;            -- 0 rows => InsufficientCreditsError, nothing written
  -- then, same transaction: INSERT ledger entry, INSERT ContactReveal, INSERT OutboxMessage
  ```

  (Equivalent alternative: `SELECT … FOR UPDATE` on the wallet, check, then update. The ledger design doc fixes which one; both are safe.)

  **Why READ COMMITTED is enough:** two transactions that update the same wallet row are serialised by the row lock. The second waits for the first to commit, then PostgreSQL **re-evaluates its `WHERE` clause against the newly committed row**, so it sees the reduced balance and either succeeds or matches 0 rows. No lost update or negative balance is possible. `CHECK (balance >= 0)` and the unique constraints (`(user, property)` on reveals, `idempotency_key` on ledger entries) are DB-level backstops. Contention exists only per wallet; 1,000 debits/s across different wallets is a commit-throughput and connection-pool question, proven by load tests (k6/Locust) in the M0 spike, M4 and M7.
- **Deviation from SRS:** the example mechanisms are replaced by a simpler one that meets the same goal. ADR-0005.
- **Affects:** FR-CRED-02.2, FR-CRED-02.3, NFR-PERF-02.1 … 02.5.
- **Status:** Proposed — awaiting stakeholder confirmation (load assumptions: OQ-09).

<a id="gap-09"></a>
### GAP-09 — "Instant allocation within 5 s, verified via the gateway's webhook"

- **Type / severity:** INFEAS · High
- **SRS text:** §6.4 "the purchased credits MUST be allocated to the user's account balance instantly (within 5 seconds). Fulfillment must be verified via the payment gateway's webhook response before the credits are applied and the user's visible balance is updated". §6.3 "utilize webhooks for robust transaction fulfillment".
- **Problem:**
  - Webhooks are asynchronous and at-least-once. They can arrive late (gateways retry with backoff for days), twice or out of order. Webhook-only fulfilment cannot guarantee 5 s.
  - "Webhook response" is ambiguous (the response is what *we* send).
  - PayPal Orders v2 needs a server-side **capture** call after the buyer approves; the capture response is itself an authoritative gateway confirmation.
- **Impact:** CRITICAL; support tickets ("I paid but have no credits"); double-crediting risk.
- **Decision:**
  - Fulfil on **whichever gateway-verified signal arrives first**:
    - (a) a signature-verified webhook (Stripe `checkout.session.completed` with `payment_status = paid`, or `payment_intent.succeeded`; PayPal `PAYMENT.CAPTURE.COMPLETED`); or
    - (b) a **server-side API verification** on the success redirect (Stripe: retrieve the Checkout Session; PayPal: capture the order and check `COMPLETED`).
  - The client is never trusted; a forged success URL grants nothing.
  - Exactly-once: `UNIQUE (gateway, gateway_payment_id)` on `PaymentOrder`, ledger idempotency key `pay:<gateway>:<gateway_payment_id>`, order transition and `PURCHASE` entry in one transaction. Amount, currency and order reference are checked first; mismatches go to `NEEDS_REVIEW`, never auto-fulfilled.
  - Reconciliation: every 5 min, orders `PENDING` for more than 10 min are re-verified with the gateway; daily reconciliation of gateway vs orders vs ledger.
  - "Within 5 s" is measured from our receipt of the first verified confirmation to the committed `PURCHASE` entry, target p99 ≤ 5 s. The return page polls order status (HTMX, 1 s) and updates the header balance.

  ```mermaid
  sequenceDiagram
      participant U as Browser
      participant A as Django (web)
      participant G as Gateway
      U->>G: Pay on hosted checkout
      G-->>U: Redirect to success URL
      U->>A: GET /payments/return/<gateway>/<order uuid>/
      A->>G: Verify / capture (server-to-server)
      G-->>A: paid
      A->>A: fulfill_order() — one transaction, idempotent
      G->>A: Webhook (later, or earlier)
      A->>A: fulfill_order() — already fulfilled, no-op
  ```

- **Deviation from SRS:** verification source widened from "webhook" to "webhook or server-side gateway API verification". Both are gateway-verified, so the integrity intent holds.
- **Affects:** FR-PAY-03.4, FR-PAY-04.1 … 04.6.
- **Status:** Proposed — awaiting stakeholder confirmation.

<a id="gap-10"></a>
### GAP-10 — Email "concurrently with the credit deduction"

- **Type / severity:** INFEAS · High
- **SRS text:** §5.5 "Concurrently with the credit deduction (2.3.3), the system MUST trigger an automated email … The email serves as a purchase receipt … and must be sent via a highly reliable, monitored transactional email service."
- **Problem:** if the email is sent during or before the commit and the transaction then rolls back, the user holds a receipt for a charge that never happened. Calling an email provider inside the request also breaks the 500 ms target and cannot scale to 1,000 reveals/s.
- **Decision:** transactional outbox (ADR-0006).
  - The reveal transaction inserts a `core.OutboxMessage` (IDs only, no PII) together with the debit, ledger entry and `ContactReveal`.
  - After commit, `transaction.on_commit` enqueues the Celery task immediately; a periodic relay sweeps anything missed.
  - The task renders and sends through django-anymail with retries and exponential backoff; a dedupe key per reveal prevents double sends.
  - Target p95 ≤ 60 s from commit to provider acceptance. A rolled-back debit never produces an email.
- **Deviation from SRS:** "concurrently" becomes "after commit, asynchronously, within seconds". The user sees the same thing.
- **Affects:** FR-CRED-03.5, FR-CRED-05.1 … 05.5, FR-NOTIF-01.
- **Status:** Proposed — awaiting stakeholder confirmation.

<a id="gap-11"></a>
### GAP-11 — "Cryptographically-linked audit trail" and "dedicated financial ledger service"

- **Type / severity:** VAGUE · High
- **SRS text:** §9.2 "The credit balance must be stored and managed securely to prevent unauthorized manipulation (e.g., using a dedicated financial ledger service or an immutable, cryptographically-linked audit trail). Regular internal audits should be performed to compare the user's live balance against the historical ledger, with automated alerts for any detected discrepancies." §5.3 "recorded in an immutable ledger".
- **Problem:** no mechanism, audit frequency or alert target is given. A hash chain stored in the same database is tamper-*evident*, not tamper-*proof*: a privileged DB user could rewrite rows and recompute hashes. Amazon QLDB, the obvious managed ledger, has been retired by AWS, and an external ledger SaaS adds a dependency to the hot path.
- **Decision:**
  - Append-only `credits.CreditLedgerEntry`; contiguous `seq` per wallet; `entry_hash = SHA-256(prev_hash ‖ canonical(entry))`, `prev_hash` = wallet head hash.
  - DB triggers and role privileges block `UPDATE`/`DELETE` (the app role has `INSERT`/`SELECT` only). Corrections only as new `REVERSAL` / `ADMIN_ADJUSTMENT` entries.
  - Audits: nightly incremental and periodic full runs recompute balance = Σ amounts, last `balance_after` = wallet balance, and verify the chain. Any discrepancy alerts on-call within 15 min, shows on the ledger-audit dashboard and freezes the wallet (`AUDIT_MISMATCH`).
  - Tamper evidence against privileged users: a periodic root hash over all wallet heads is written to S3 with Object Lock (WORM) (`LedgerAnchor`); `pgaudit` alarms on `DISABLE TRIGGER`, `GRANT` and `SET ROLE`.
- **Affects:** FR-CRED-03.3, FR-CRED-07.5, NFR-SEC-02.1 … 02.6, FR-OPS-06.1.
- **Status:** Proposed — awaiting stakeholder confirmation.

<a id="gap-12"></a>
### GAP-12 — "AES-256 at rest" and "PII tokenized or pseudonymized"

- **Type / severity:** VAGUE · High
- **SRS text:** §9.1 "All sensitive user data (passwords, payment information, contact numbers, PII) must be encrypted both in transit (mandatory TLS/SSL v1.2+) and at rest (AES-256 standard). Personal Identifiable Information (PII) must be tokenized or pseudonymized whenever possible within the application's storage layer".
- **Problem:**
  1. Passwords must be **hashed**, never encrypted (encryption is reversible).
  2. Payment card data must not be stored at all (GAP-14, SAQ A), so there is nothing to encrypt.
  3. Storage encryption alone (disk/KMS) protects against stolen media and snapshots, but not against SQL access through a compromised app or credential.
  4. Field-level encryption breaks equality lookups (login, uniqueness, fraud matching) unless blind indexes are added.
  5. "Tokenized" suggests a token vault: a new service and availability dependency.
  6. "SSL" is obsolete; only TLS 1.2+ is acceptable.
- **Decision (layered):**

  | Layer | Applies to | Mechanism |
  |---|---|---|
  | Transport | All traffic | TLS ≥ 1.2 at CloudFront and ALB, HSTS; TLS to RDS and ElastiCache |
  | Storage encryption | Everything at rest | KMS AES-256 on RDS (incl. replicas, snapshots, backups), S3, ElastiCache |
  | Field-level encryption | Listing contact phone/email, user phone, reveal contact snapshots, webhook payloads | AES-256-GCM envelope encryption (data key wrapped by KMS), versioned ciphertext for key rotation (ADR-0010) |
  | Blind indexes | Where equality lookups are needed: verified phone uniqueness, promo claims, contact fraud matching | HMAC-SHA256 with a separate key and per-purpose prefix |
  | Pseudonymisation | Logs, analytics, outbox payloads, URLs | Public UUIDs; no PII in logs/traces (redaction) |
  | Passwords | — | Argon2id hashes (GAP-07) |
  | Payment data | — | Not stored; gateway IDs, card brand and last 4 only |

  No separate tokenisation vault (security doc DEV-SEC-4).
- **Login email — baseline vs proposed change:**
  - **Baseline:** login email field-level encrypted with an HMAC blind index for lookups.
  - **Proposed change** (architecture AR-4, ADR-0010, security DEV-SEC-5, domain model OQ-DM-04): keep the login email **in plaintext under storage encryption only**, protected by DB role separation, access control and log redaction. Reason: django-allauth looks up emails case-insensitively in several places (including its `EmailAddress` model), so encrypting it means invasive adapter overrides that every allauth upgrade can break; support also needs to search by email. Estimated cost of the baseline: about 3–5 extra days in M1 plus upgrade risk.
  - **Requirements view:** the SRS says "whenever possible", which leaves room for the proposed change. The domain model has already drafted the schema with the proposed change. This must be decided before the `accounts` migrations reach a shared environment with real data.
- **Affects:** NFR-SEC-01.1 … 01.7, FR-LIST-02.7, FR-LIST-02.8.
- **Status:** Proposed — awaiting stakeholder confirmation. **Blocking for M1** (OQ-29).

<a id="gap-13"></a>
### GAP-13 — Localised currency "determined by their IP or account region settings"

- **Type / severity:** VAGUE · Medium
- **SRS text:** §6.2 "multiple, distinct credit packages (e.g., 20 credits, 50 credits, 120 credits) with associated pricing … volume discounts … prices dynamically displayed in the user's localized currency determined by their IP or account region settings."
- **Problem:** "dynamically" could mean live FX conversion: prices that change daily, odd amounts (₹1,673.42), FX risk, currencies the gateways cannot settle, and tax confusion. Precedence between IP and account region is not stated, and IP-based pricing invites VPN arbitrage. No actual prices are given.
- **Decision:**
  - Explicit per-currency **price book** `payments.CreditPackagePrice(package, currency, amount_minor, valid_from, valid_to)`, maintained by Finance, audited, no deploy needed, no live FX.
  - Resolution order: account region/currency setting → GeoIP country (MaxMind GeoLite2) → market default. Only currencies present in the price book and supported by the chosen gateway are offered.
  - The charged amount and currency equal the displayed ones (snapshot on `PaymentOrder`).
  - Volume discounts validated per currency (per-credit price strictly decreasing with package size).
  - Arbitrage control: region currency plus market default only; region locked after the first purchase (security OQ-SEC-04 default).
- **Deviation from SRS (interpretation):** "dynamically" means "resolved per request from the price book", not FX conversion.
- **Affects:** FR-PAY-02.1 … 02.7.
- **Status:** Proposed — awaiting stakeholder confirmation (prices OQ-03, currencies OQ-04).

<a id="gap-14"></a>
### GAP-14 — "At least two major, globally recognized payment gateways"

- **Type / severity:** VAGUE · Medium
- **SRS text:** §6.3 "integrate with at least two major, globally recognized payment gateways (e.g., Stripe, PayPal, or local equivalent) … secure tokenization of payment data and utilize webhooks". §9.3 "never stores, transmits, or processes raw credit card data".
- **Problem:** the two gateways are examples, not decisions. Gateway availability and preferred payment methods vary by country, and some markets favour local methods.
- **Decision:**
  - A `PaymentGateway` interface (create checkout, verify payment, verify and parse webhook, refund, fetch status) with a shared contract test suite.
  - Adapters: **Stripe Checkout** (hosted page, keeps us in PCI DSS SAQ A scope) and **PayPal Orders v2** (hosted approval plus server-side capture). **Razorpay** is an optional "local equivalent" adapter (for example for India).
  - The application never renders card fields and never touches raw card data.
- **Affects:** FR-PAY-03.1 … 03.6, NFR-SEC-03.
- **Status:** Proposed — awaiting stakeholder confirmation (per-market gateways and methods: OQ-07).

<a id="gap-15"></a>
### GAP-15 — "At least 90 % unit test and integration test coverage"

- **Type / severity:** VAGUE · Low
- **SRS text:** §10.2 "maintain at least 90% unit test and integration test coverage."
- **Problem:** the measure (line or branch) and the scope (which code) are undefined. A 90 % gate over the whole repository, including migrations, settings and admin wiring, rewards low-value tests; coverage alone says nothing about test quality.
- **Decision:**
  - CI gate **≥ 90 % line + branch on domain code** (models, services, selectors, gateways, tasks).
  - **≥ 85 % on the whole repository** excluding migrations, settings and generated files, ratcheting upwards (never allowed to drop).
  - Every CRITICAL requirement must have linked passing tests (requirement → test traceability matrix in CI).
- **Deviation from SRS (partial):** the whole-repo threshold starts at 85 % rather than 90 %.
- **Affects:** NFR-CODE-01.3.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-30).

<a id="gap-16"></a>
### GAP-16 — The Availability section has no availability targets

- **Type / severity:** MISSING · Medium
- **SRS text:** §8.3 "The backup procedure must include regular database restoration testing … Detailed runbooks must be created for common incident response scenarios (e.g., payment API failure, database performance degradation)".
- **Problem:** no SLA, uptime, RPO or RTO. Infrastructure topology, cost and on-call depend on these numbers.
- **Decision (proposed targets):**

  | Metric | Proposed | Mechanism |
  |---|---|---|
  | Availability (monthly) | **99.9 %** (≈ 43 min downtime per month) | Multi-AZ RDS, ≥ 2 web tasks across AZs, rolling deploys |
  | RPO | **≤ 5 min** | RDS automated backups + point-in-time recovery |
  | RTO | **≤ 1 h** | Restore runbook, rehearsed in M7 and then quarterly |
  | Regional disaster | RPO ≤ 1 h, RTO ≤ 8 h | Cross-region snapshot copies (architecture A-5) |

- **Affects:** NFR-AVAIL-01.1 … 01.8.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-08).

<a id="gap-17"></a>
### GAP-17 — Latency targets are not measurable as written

- **Type / severity:** VAGUE · High
- **SRS text:** §8.1 "All property search queries and credit transactions must complete within 500ms under standard load conditions, and not exceed 1000ms during peak load … achieved through optimized database indexing, read-replicas, and efficient content delivery network (CDN) caching for static assets." §4.5 "The underlying search index must be optimized for fast, relevant results".
- **Problem:**
  - "All" read literally means 100 % of requests, which no system can guarantee (tail latency, cold caches, deploys).
  - The measurement point is not stated: server time, or end-to-end including the user's mobile network.
  - "Standard" and "peak" load are not defined.
  - "Search index" might be read as requiring a separate search engine.
- **Decision:**
  - Targets are **server-side p95** (ALB target response time and OTel request span): ≤ 500 ms at standard load, ≤ 1,000 ms at peak; p99 is reported and alerted on but has no contractual target.
  - Standard/peak load from OQ-09. Until answered: 50 search requests/s standard and 5× that at peak (architecture A-4 assumption).
  - Means: PostgreSQL 17 + PostGIS (GiST on `geography`), `pg_trgm` (GIN) for fuzzy text, full-text `tsvector` (GIN), Valkey cache for hot searches (TTL 60 s), search reads on the read replica, CloudFront for static and media. OpenSearch only when measured triggers are hit (ADR-0004).
  - Browser experience is covered separately by Core Web Vitals budgets (NFR-PERF-01.6).
- **Deviation from SRS:** "all … must complete within" becomes a p95 target, measured server-side.
- **Affects:** NFR-PERF-01.1 … 01.6, FR-LIST-05.10.
- **Status:** Proposed — awaiting stakeholder confirmation.

<a id="gap-18"></a>
### GAP-18 — Capabilities that appear only in the diagrams

- **Type / severity:** DIAGRAM · Medium
- **Diagram text (SRC-03):** "Ops Console (Monitor & manage jobs, listing moderation, fraud review)", "Verification API (Owner identity & listing checks)", "Asset Storage … KYC Docs, Ownership Proofs", "lead forms", "lead form processing", "Notification Services (Lead alerts, …)", "Maps & Geocoding API (Address geocoding, map tiles)".
- **Problem:** none of these is in the SRS, yet the SRS needs some of them: §4.3's "formal administrative review" requires a staff tool, and §9.2's audits need somewhere to show results.
- **Decision:**

  | Capability | MVP? | Milestone | Reason |
  |---|---|---|---|
  | Ops console (hardened Django admin + custom staff views): moderation queue, tag-change review, fraud flags, ledger-audit dashboard, jobs monitor, support lookup, four-eyes credit adjustments | **Yes** | M1 (hardened admin) → M6 | Needed by SRS §4.3 and §9.2 |
  | Verification / KYC API, KYC docs, ownership proofs | Post-MVP | — | Storage and hooks now: private bucket, signed URLs (FR-KYC-01.3) |
  | Lead forms / free inquiry | Post-MVP | — | GAP-01 |
  | Lister lead alerts | Post-MVP | — | GAP-59 |
  | Map tiles | Open | M3 | OQ-27 (cost and provider terms) |

- **Affects:** FR-OPS-01 … 07, FR-KYC-01, FR-LEAD-01.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-20, OQ-21, OQ-17).

<a id="gap-19"></a>
### GAP-19 — "Saves" metric without a save feature

- **Type / severity:** MISSING · Low
- **SRS text:** §4.4 "real-time visibility metrics (views, saves, clicks on 'Show Number')".
- **Problem:** nothing in the SRS lets a renter save a property, so the metric cannot exist.
- **Decision:** add **Saved properties** (FR-SAVE-01) in M3: save toggle on cards and the detail page, a saved list page, `UNIQUE (user, property)`; counts feed the listing metric. Saving requires a verified account (baseline; OQ-42 allows "login only").
- **Status:** Proposed — awaiting stakeholder confirmation.

<a id="gap-20"></a>
### GAP-20 — Contact information as a mandatory listing field

- **Type / severity:** VAGUE · High
- **SRS text:** §4.2 "mandatory fields for property address, type, price, description, images …, and contact information (phone/email)". §5.4 "display the property lister's phone number and/or email address".
- **Problem:** account-level or listing-level? Which of phone/email is mandatory? Agents may use an office number. Most importantly, any leak of the contact before payment (hidden DOM element, JSON-LD, Open Graph tags, an HTMX fragment, a cached page) makes the paywall trivially bypassable.
- **Decision:**
  - Contact is **listing-level** (`contact_name`, `contact_phone` required, `contact_email` optional — OQ-37), defaulting from the lister's profile.
  - The phone is OTP-verified when it differs from the verified account phone (GAP-63).
  - Stored with field-level encryption (GAP-12).
  - **Never rendered** in HTML (not even hidden), JSON, JSON-LD, OG tags, HTMX fragments, sitemaps, search results, caches, logs or analytics until the viewer has a `ContactReveal` for that property, owns it, or is staff with permission. Decryption happens in one selector only; reveal responses carry `Cache-Control: no-store`. An automated test searches rendered responses for the stored values.
- **Affects:** FR-LIST-02.7, FR-LIST-02.8, FR-CRED-04.
- **Status:** Proposed — awaiting stakeholder confirmation.

<a id="gap-21"></a>
### GAP-21 — Image rules without values

- **Type / severity:** VAGUE · Medium
- **SRS text:** §4.2 "images (minimum 3, maximum 20) … Image uploads must handle various formats efficiently, enforce aspect ratios, respect a maximum file size (e.g., 5MB), and include automatic thumbnail generation for optimal display performance across all device types."
- **Problem:** formats are unspecified; "enforce aspect ratios" gives no ratios; "e.g., 5MB" is an example, not a limit. Processing in the web tier would hurt latency and expose the server to image-parser exploits and decompression bombs. Phone photos carry EXIF GPS that would reveal an owner's home location.
- **Decision** (listings design §8 is authoritative):
  - Direct-to-S3 presigned POST with a 5 MiB (5,242,880-byte) size condition; also checked in the browser and after upload.
  - Celery post-processing: Pillow decode/verify, 50 MP pixel cap, EXIF orientation applied, all metadata stripped (EXIF incl. GPS, XMP, IPTC), sRGB, resized WebP variants (`thumb`, `card`, `md`, `lg`, `og`) plus a JPEG `email` variant. Any failure rejects the image with a clear reason. Originals are never served.
  - Formats: JPEG, PNG, WebP. HEIC is a stretch goal (OQ-23).
  - Aspect ratio (r = width/height): 1.30–1.80 accepted; 1.00–1.30 auto-cropped to 4:3; 1.80–2.40 auto-cropped to 16:9; portrait (< 1.00) and panoramas (> 2.40) rejected server-side, with an in-browser crop tool offered before upload. Minimum size: long edge ≥ 1,024 px, short edge ≥ 576 px.
  - 3–20 images: publish blocked below 3 `READY` images; the 21st is refused under a row lock.
- **Consistency note:** [Development Approach §7.4](../delivery/01-development-approach.md) states "Aspect ratio 3:4 to 2:1 (US-206)". That conflicts with the listings design (portrait rejected) and cites the wrong story (US-206 is the tag story). See CI-03.
- **Affects:** FR-LIST-02.6, FR-LIST-02.10 … 02.15.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-23).

<a id="gap-22"></a>
### GAP-22 — Lister tag change needs a "formal administrative review"

- **Type / severity:** VAGUE · Medium
- **SRS text:** §4.3 "The listing form MUST require the lister to select one of two exclusive tags … 'AgentListed' or 'OwnerListed.' … the selection cannot be modified without a formal administrative review process".
- **Problem:** the process is undefined: who requests, who decides, what evidence, how fast, whether drafts are affected, what happens to existing reveals.
- **Decision:**
  - The tag can be edited freely while the listing has never been published. After first publish it is immutable: read-only in forms, rejected by the service (`ListerTagImmutableError`), guarded by a DB trigger.
  - Changes go through `listings.PropertyTagChangeRequest` (target tag, reason, optional evidence in the private bucket). At most one pending request per listing; 14-day cooldown after a rejection.
  - A Moderator approves or rejects with a note. Approval changes the tag in the same transaction and writes an `AuditLog` entry. The lister is notified either way.
  - Existing reveals and ledger entries are unaffected.
  - Delivery: M2 as an admin action; M6 as a dedicated queue with SLA (default 2 business days).
- **Affects:** FR-LIST-03.1 … 03.5, FR-OPS-03.1.
- **Status:** Proposed — awaiting stakeholder confirmation (SLA OQ-18; tag semantics OQ-36).

<a id="gap-23"></a>
### GAP-23 — Social sign-on is both "(optional)" and "must"

- **Type / severity:** CONTRA · Low
- **SRS text:** §3.1 "(optional) It must also support modern Social Sign-On (SSO) options like Google and Apple". HLRD: "Must support Social Sign-On (SSO) (Google/Apple)(Optional)."
- **Problem:** the modality contradicts itself. Each provider brings setup and review work (Google OAuth consent screen verification, an Apple Developer Program membership, Apple private-relay emails).
- **Decision:** priority **Could**. Delivered as an M1 stretch goal if the milestone goal is met, otherwise Post-MVP. allauth's social tables are migrated from M1 so adding a provider later is configuration plus tests.
- **Affects:** FR-AUTH-02.1 … 02.3, FR-AUTH-05.2.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-14).

<a id="gap-24"></a>
### GAP-24 — Social account linking and verification semantics

- **Type / severity:** MISSING · Medium
- **SRS text:** none beyond §3.1 and §3.4 "secure login via verified credentials or social sign-on".
- **Problem:** auto-linking a social login to an existing local account by email, when the provider has not verified that email, allows account takeover. Whether a social sign-up counts as "verified" is also unstated. Apple "Hide My Email" relay addresses are unique per app, which could be used to farm promo credits.
- **Decision:** link only when the provider asserts a verified email that matches a verified local email; treat a social account as verified only on a provider-verified email; promo eligibility goes through `SignupPromoClaim` and the anti-abuse controls (GAP-06) unchanged.
- **Affects:** FR-AUTH-02.3.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-14).

<a id="gap-25"></a>
### GAP-25 — "UI/UX Recommendations" contains MUST statements

- **Type / severity:** DEFECT · Low
- **SRS text:** §11.0 is titled "Recommendations", yet §11.1 says "The user's current credit balance MUST be displayed prominently and persistently" and §11.2 says components "must be designed and optimized for mobile devices".
- **Problem:** readers could treat the whole section as optional.
- **Decision:** modality is decided per sentence: MUST/must and "Ensure" → **Must**; should → **Should**. Applied in NFR-UX-01 … 06.
- **Status:** Proposed — awaiting stakeholder confirmation (editorial).

<a id="gap-26"></a>
### GAP-26 — Verification by email **or** phone

- **Type / severity:** VAGUE · Medium
- **SRS text:** §3.2 "The system shall require email confirmation or phone number verification (using a one-time passcode/OTP) to activate the account." §5.5 email sent "to the logged-in user's registered email address".
- **Problem:** does either method suffice? Is a phone collected at sign-up? A phone-only verified user has an unverified email address: sending reveal receipts (which contain a lister's contact, GAP-36) to a mistyped address would leak lister data to a stranger, and password reset by email would be unreliable.
- **Decision:**
  - **Assumption:** either method activates the account. Email verification is the default path at sign-up; phone OTP (Twilio Verify) is the alternative.
  - If only the phone is verified, reveal emails are **held** until the email is verified, and the UI says so (GAP-37). Password reset uses only verified channels.
  - A phone number can belong to only one verified account (blind index).
- **Affects:** FR-AUTH-03.2, FR-AUTH-03.3, FR-CRED-05.1.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-10).

<a id="gap-27"></a>
### GAP-27 — Password "complexity rules" unspecified

- **Type / severity:** VAGUE · Low
- **SRS text:** §3.1 "validating input for format, password strength (including complexity rules) … in real-time".
- **Problem:** no rules are given. Character-composition rules ("must contain a digit and a symbol") are discouraged by NIST SP 800-63B because they push users to predictable patterns; length plus blocklists works better.
- **Decision:** **Assumption:** minimum 12 characters; not in the common-password list; not similar to name or email; not all numeric; no composition rules. A strength meter and a live rule checklist give the real-time feedback the SRS asks for. If stakeholders do require composition rules, adding them is a validator change.
- **Affects:** FR-AUTH-01.3.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-15).

<a id="gap-28"></a>
### GAP-28 — Real-time email-uniqueness check enables account enumeration

- **Type / severity:** INFEAS · Medium
- **SRS text:** §3.1 "validating input for … email uniqueness in real-time".
- **Problem:** an endpoint that answers "this email is taken" tells an attacker which emails have accounts (an OWASP-listed weakness), which helps credential stuffing and targeted phishing. It also undermines the generic messages used on login and password reset.
- **Decision:** keep the SRS behaviour with mitigations: per-IP and per-session rate limits, a Turnstile challenge after a threshold, WAF rate rules, monitoring, and the check only on the sign-up form. The enumeration-safe alternative (allauth's prevent-enumeration flow, which emails the existing owner instead of showing an error) is offered as an option.
- **Affects:** FR-AUTH-01.4.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-15; security OQ-SEC-02).

<a id="gap-29"></a>
### GAP-29 — "Transactional activities" is not defined

- **Type / severity:** VAGUE · Medium
- **SRS text:** §3.2 "restricted from transactional activities (like listing or consuming credits)".
- **Problem:** "like" makes the list open-ended.
- **Decision:** unverified users **may** browse, search, view listings, edit their profile, verify, log out and request deletion. They **may not** create or publish listings, request tag changes, use Show Number, purchase credits, save properties or report listings, and they receive no promo credits. Purchases are blocked because the wallet is created at verification (GAP-53). Enforced in services (`can_transact(user)`), with a matrix test over every protected action.
- **Affects:** FR-AUTH-03.4, FR-AUTH-03.5.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-10).

<a id="gap-30"></a>
### GAP-30 — Can unverified users log in?

- **Type / severity:** CONTRA · Medium
- **SRS text:** §3.3 "Upon the first successful login after registration"; §3.4 "secure login via verified credentials".
- **Problem:** "verified credentials" could mean only verified accounts may log in (allauth's mandatory-verification mode blocks login until the email is confirmed). But phone OTP verification and "resend link" need a logged-in session, and §3.3 assumes logins can happen right after registration.
- **Decision:** unverified users can log in into a **restricted** state (GAP-29) so they can complete verification. "Verified credentials" means a correct password or a valid social assertion. Unverified accounts are purged after 7 days (GAP-60).
- **Affects:** FR-AUTH-05.1.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-10).

<a id="gap-31"></a>
### GAP-31 — Refunds and chargebacks are not covered

- **Type / severity:** MISSING · High
- **SRS text:** none. §6.3 mentions "timely error management"; §9.2 requires integrity.
- **Problem:** gateways will deliver refunds and disputes; renters will complain about wrong numbers. By then purchased credits may already be spent, and the ledger cannot go negative or be edited.
- **Decision:**
  - A gateway refund or dispute creates a `REVERSAL` entry for the purchased credits, capped at the current balance (never below 0). The shortfall is recorded, the order moves to `REFUNDED`/`DISPUTED`, and the wallet can be frozen (`CHARGEBACK`) for Finance review.
  - No self-service refunds in MVP. Finance issues refunds through the gateway.
  - Reveal refunds (for example an invalid contact) are staff `ADMIN_ADJUSTMENT` entries with reason code `INVALID_CONTACT_REFUND` and four-eyes approval; the revealed contact stays visible.
  - **Assumption:** if EU/UK consumers are in scope, checkout asks for the express consent and acknowledgement that consumer law requires before immediate supply of digital content removes the withdrawal right. Legal to confirm.
- **Affects:** FR-PAY-06.1 … 06.3, FR-OPS-06.2.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-05).

<a id="gap-32"></a>
### GAP-32 — Do credits expire?

- **Type / severity:** MISSING · Medium
- **SRS text:** none.
- **Problem:** unexpired credits are a financial liability, and some jurisdictions regulate the expiry of prepaid value. Expiry also changes the ledger (an `EXPIRY` entry type and per-lot tracking).
- **Decision:** **Assumption:** credits (promo and purchased) never expire in MVP. The entry-type design allows adding `EXPIRY` later.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-12).

<a id="gap-33"></a>
### GAP-33 — "The server process ID"

- **Type / severity:** VAGUE · Low
- **SRS text:** §5.3 "including a unique transaction ID, user balance before/after, timestamp, the specific property ID, and the server process ID for financial auditing, non-repudiation, and regulatory traceability."
- **Problem:** OS process IDs inside containers are small and reused in every task (often PID 1). On its own a PID identifies nothing.
- **Decision:** every ledger entry records `server_process_id` = `<service>:<task-id>:<pid>` (for example `web:3f9c2a1b:4127`), plus `request_id` (HTTP request ID or Celery task ID) and `app_release` (Git SHA of the image). The catalog's term "process identity / `process_info`" refers to these three fields; the domain model is the schema of record (CI-02).
- **Affects:** FR-CRED-03.2.
- **Status:** Proposed — awaiting stakeholder confirmation.

<a id="gap-34"></a>
### GAP-34 — Revealed contact "accessible … without further cost" over time

- **Type / severity:** VAGUE · Medium
- **SRS text:** §5.4 "must remain accessible within the user's transaction history view for future reference without further cost."
- **Problem:** the lister may later change the contact, the listing may be rented or archived, or the lister's account may be erased. Which contact is shown, and how long may a copy of someone's phone number be kept?
- **Decision:** an encrypted contact snapshot (name, phone, email) is stored on the `ContactReveal` and kept 24 months, then removed (domain model §15). History shows the snapshot; if the listing is still published and the contact has changed, the current contact is shown too, free. Snapshots follow the erasure rules of the domain model (§14).
- **Affects:** FR-CRED-04.2, FR-CRED-04.4.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-13).

<a id="gap-35"></a>
### GAP-35 — Show Number on "all property listings"

- **Type / severity:** VAGUE · Low
- **SRS text:** §5.1 "all property listings, the primary call-to-action button for accessing the lister's contact information shall be labeled 'Show Number.'"
- **Problem:** "listings" could mean search-result cards as well as detail pages. Paying from a card skips the property details the renter is paying about and invites accidental spending.
- **Decision:** Show Number is the primary CTA on the **listing detail page** (sticky on mobile). Cards link to the detail page; there is no reveal from cards.
- **Deviation from SRS (interpretation):** "all property listings" is read as "every listing's detail page".
- **Affects:** FR-CRED-01.1.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-44).

<a id="gap-36"></a>
### GAP-36 — The reveal email does not list the contact itself

- **Type / severity:** MISSING · Medium
- **SRS text:** §5.5 "an automated email containing the property details (link, lister name, listing title, full description) and a transaction confirmation … The email serves as a purchase receipt, a persistent record of the lead".
- **Problem:** a "persistent record of the lead" without the phone/email the user paid for is of little use. Including it puts lister PII into an inbox we do not control.
- **Decision:** the email **includes the revealed contact** (phone and/or email) together with the SRS fields and the transaction confirmation (transaction ID, credits deducted, balance after, date/time). Plain-text and HTML parts; no tracking pixels. Held until the email address is verified (GAP-26).
- **Affects:** FR-CRED-05.2.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-34).

<a id="gap-37"></a>
### GAP-37 — The fixed confirmation copy is sometimes false

- **Type / severity:** CONTRA · Low
- **SRS text:** §11.1 "display a minimal, non-modal confirmation message (e.g., a toast notification) stating: 'Contact revealed. 2 credits deducted. Details emailed to you.'"
- **Problem:** the text is wrong when the contact is shown again for free (nothing deducted), when the email is held (GAP-26), or if the cost changes (GAP-64).
- **Decision:** exact SRS copy for a paid reveal; variants otherwise: free re-view shows no toast (or "Contact shown. No credits used."); held email shows "Contact revealed. 2 credits deducted. Verify your email to receive the details." The number comes from the cost setting.
- **Affects:** NFR-UX-02.1, NFR-UX-02.2.
- **Status:** Proposed — awaiting stakeholder confirmation.

<a id="gap-38"></a>
### GAP-38 — Reveals on rented, unlisted or suspended listings

- **Type / severity:** VAGUE · Medium
- **SRS text:** §5.1 "all property listings …".
- **Problem:** charging for the contact of a rented or suspended listing sells a dead or risky lead.
- **Decision:** only `PUBLISHED` listings offer Show Number; the reveal service rejects any other status. Other statuses show "No longer available". Users who revealed earlier keep free access to the contact.
- **Deviation from SRS (interpretation):** narrows "all property listings" to live listings.
- **Affects:** FR-CRED-01.7.
- **Status:** Proposed — awaiting stakeholder confirmation.

<a id="gap-39"></a>
### GAP-39 — Listing metrics "instantly" in "real-time"

- **Type / severity:** INFEAS · Low
- **SRS text:** §4.4 "real-time visibility metrics (views, saves, clicks on 'Show Number') instantly."
- **Problem:** true real-time needs push (WebSockets/SSE) and a database write per page view on the hottest read path. The diagram itself specifies "Periodic HTTP Polling".
- **Decision:** views and Show Number clicks are counted in Valkey and flushed every 60 s to `analytics.PropertyDailyStat` (≤ 60 s freshness); saves and reveals are exact DB counts (immediate). The dashboard refreshes by HTMX polling every 30 s while the tab is visible.
- **Deviation from SRS:** "instantly" means "within 60 s" for counters.
- **Affects:** FR-LIST-04.7 … 04.10.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-38).

<a id="gap-40"></a>
### GAP-40 — Metric definitions

- **Type / severity:** VAGUE · Low
- **SRS text:** §4.4 "views, saves, clicks on 'Show Number'"; §7.2 "listing views, contact reveals, and overall performance metrics, for listers to effectively track ROI".
- **Problem:** do owner views or bots count? Repeated views? Are "clicks" the same as "reveals"? What is "overall performance" or "ROI" when listers pay nothing in MVP?
- **Decision** (listings design §10.2): **view** = detail render by a non-owner, non-bot viewer, deduplicated per viewer per 30 min; **save** = current saved count; **Show Number click** = every click by a logged-in non-owner, including insufficient-credit outcomes; **reveal** = successful paid reveal. "Overall performance" = 30-day totals and the reveal/view ratio. Under renter-pays, a lister's "ROI" is engagement, not money.
- **Affects:** FR-LIST-04.7 … 04.9, FR-PROF-02.9.
- **Status:** Proposed — awaiting stakeholder confirmation.

<a id="gap-41"></a>
### GAP-41 — What "location" means in search

- **Type / severity:** VAGUE · Medium
- **SRS text:** §4.5 "search and filter properties based on location … using geospatial queries".
- **Problem:** free text, city, locality, postcode, map area, radius or "near me" are all possible readings.
- **Decision** (search design §5): place text is resolved via autocomplete on listing localities with a geocoder fallback. A city match searches the whole city (equality on the normalised city name); a point (locality, geocoded address or opt-in "near me") uses a radius of 2/5/10/25/50 km (default 10 km) with `ST_DWithin` on a GiST index. One market per search. Map-viewport search is Post-MVP (OQ-27).
- **Affects:** FR-LIST-05.3.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-27, OQ-33).

<a id="gap-42"></a>
### GAP-42 — Price filter across currencies and rent periods

- **Type / severity:** VAGUE · Low
- **SRS text:** §4.5 "price range".
- **Problem:** a multinational catalogue mixes currencies and monthly/weekly rents; a single price range across them needs FX and period conversion.
- **Decision:** listing currency is derived from the listing's country; search is scoped to one market; the price filter uses `rent_monthly_minor` (weekly × 52 / 12) in the market currency. No FX anywhere.
- **Affects:** FR-LIST-05.4.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-33).

<a id="gap-43"></a>
### GAP-43 — Minimal listing attributes and no property-type list

- **Type / severity:** MISSING · Medium
- **SRS text:** §4.2 mandatory "property address, type, price, description, images … and contact information".
- **Problem:** renters expect bedrooms, bathrooms, area, furnishing, availability date and deposit; the property types are not listed; commercial and short-term rentals are neither in nor out. The reveal email needs a "listing title" (§5.5) that §4.2 does not require.
- **Decision:** add a mandatory **title** (10–100 chars). Optional attributes: bedrooms, bathrooms, area (m² or ft²), furnishing, available-from date, deposit. Property types: Apartment, Studio, House, Townhouse, Villa, Room, Shared accommodation. **Assumption:** residential long-term rentals only; rent period monthly (default) or weekly.
- **Affects:** FR-LIST-02.2 … 02.5.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-24).

<a id="gap-44"></a>
### GAP-44 — Client-side validation and drafts

- **Type / severity:** VAGUE · Low
- **SRS text:** §4.1 "allow listers to save progress as a draft … and must include robust client-side validation for necessary fields before server submission."
- **Problem:** client-side validation alone can be bypassed; and a draft is by definition incomplete, so "necessary fields" cannot apply on every save.
- **Decision:** client-side validation (HTML5 + Alpine.js inline messages) for UX; the server re-validates every rule. Drafts are saved server-side from creation with lenient validation (only valid fields are stored); strict validation runs on step completion and publish. Maximum 10 open drafts per user.
- **Affects:** FR-LIST-01.3 … 01.5.
- **Status:** Proposed — awaiting stakeholder confirmation.

<a id="gap-45"></a>
### GAP-45 — Listing expiry and draft retention

- **Type / severity:** MISSING · Medium
- **SRS text:** none (§4.4 lists only "mark as rented, or unlist").
- **Problem:** listers often forget to mark a property as rented. Stale listings make renters pay 2 credits for dead leads, which drives refunds and distrust.
- **Decision:** **Assumption:** published listings expire after 60 days without renewal, with a reminder 7 days before and one-click renew; three "already rented" reports auto-unlist a listing. Idle drafts are archived after 90 days (reminder at day 80) and never-published archived drafts are deleted 30 days later.
- **Affects:** FR-LIST-04.11, FR-LIST-04.12.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-26).

<a id="gap-46"></a>
### GAP-46 — Listing moderation policy

- **Type / severity:** MISSING · Medium
- **SRS text:** none, except tag-change review (§4.3). SRC-03: "listing moderation, fraud review".
- **Problem:** reviewing every listing before publishing delays listers; publishing without review lets renters pay for scam listings.
- **Decision:** post-publish moderation with **risk-based pre-moderation** (setting `LISTINGS_PREMODERATION_MODE`, default `flagged_only`; `first_listing` or `all` switchable without a deploy). Automated checks on submit/edit route risky listings to `PENDING_REVIEW`; renter reports open moderation cases; bad reveals can be refunded (GAP-31).
- **Affects:** FR-LIST-01.6, FR-OPS-02.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-19, OQ-40).

<a id="gap-47"></a>
### GAP-47 — "Persistent dropdown"

- **Type / severity:** VAGUE · Low
- **SRS text:** §7.1 "Clicking the Profile Icon shall reveal a persistent dropdown menu".
- **Problem:** "persistent" could mean always open, sticky, or "doesn't close when the pointer leaves".
- **Decision:** the header and profile icon are present on every page; the dropdown opens on click/tap/Enter/Space and stays open until dismissed (Escape, outside click, selecting an item). No hover behaviour. The balance is also shown persistently in the header itself (NFR-UX-01).
- **Affects:** FR-PROF-01.5.
- **Status:** Proposed — awaiting stakeholder confirmation.

<a id="gap-48"></a>
### GAP-48 — "Secure two-step processes" for sensitive changes

- **Type / severity:** VAGUE · Medium
- **SRS text:** §7.2 "secure two-step processes for changing sensitive fields like email/password".
- **Problem:** the steps are not defined (and "two-step" is not two-factor authentication).
- **Decision:**
  - **Email:** re-authenticate (within 10 min) → confirmation link to the new address → switch only after confirmation → notice to the old address.
  - **Password:** current password + new password → all other sessions revoked → notification email.
  - **Phone:** OTP to the new number; the old number stays active until the new one is verified.
  - All changes are audited. User-facing MFA is Post-MVP (GAP-62).
- **Affects:** FR-PROF-02.4 … 02.6.
- **Status:** Proposed — awaiting stakeholder confirmation.

<a id="gap-49"></a>
### GAP-49 — Logout: "invalidate all active session tokens"

- **Type / severity:** VAGUE · Medium
- **SRS text:** §7.3 "securely terminate the user's session on the server side, invalidate all active session tokens, and clear any associated local authentication artifacts."
- **Problem:** "all" could mean the tokens of this login or every session on every device. Logging users out everywhere on every logout is hostile for multi-device users.
- **Decision:** Logout (a POST with CSRF) deletes the current server session, expires cookies, sends `Clear-Site-Data: "cache", "cookies", "storage"`; authenticated pages carry `Cache-Control: no-store`. A separate "Sign out of all devices" action revokes every session (allauth user sessions). A password change or reset revokes all other sessions automatically. Staff sessions time out after 30 min idle.
- **Affects:** FR-PROF-03.1 … 03.5, FR-AUTH-05.6.
- **Status:** Proposed — awaiting stakeholder confirmation.

<a id="gap-50"></a>
### GAP-50 — "Password" listed as a viewable personal detail

- **Type / severity:** DEFECT · Low
- **SRS text:** §7.2 "Allows the user to view and edit personal details (Name, Email, Phone, Password)."
- **Problem:** passwords are hashed and cannot be viewed; social-only accounts have no password.
- **Decision:** password is change-only ("Change password", or "Set password" for social-only accounts). Phone is shown masked except the last digits.
- **Affects:** FR-PROF-02.2.
- **Status:** Proposed — awaiting stakeholder confirmation.

<a id="gap-51"></a>
### GAP-51 — Privacy and data protection are not mentioned

- **Type / severity:** MISSING · High
- **SRS text:** none, although §1.0 targets "multinational traffic" and the product sells access to personal contact details.
- **Problem:** depending on markets, laws such as the EU/UK GDPR, India's DPDP Act 2023 or US state privacy laws apply: lawful basis and consent (cookies, marketing), data-subject rights, retention, breach notification, processor agreements and cross-border transfers.
- **Decision:** privacy-by-design baseline: versioned Terms and Privacy acceptance at sign-up; essential cookies only by default (consent banner if non-essential cookies or RUM are added); marketing opt-in off by default; data map and retention schedule enforced by jobs; data-subject requests handled by Support in MVP (self-service later unless law requires it); processor inventory (AWS, Stripe, PayPal, Twilio, SES/Mailgun, Sentry, MaxMind, the maps provider).
- **Affects:** NFR-SEC-05.1 … 05.4, FR-PROF-02.7.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-28).

<a id="gap-52"></a>
### GAP-52 — "Multinational" without languages or locales

- **Type / severity:** MISSING · Medium
- **SRS text:** §1.0 "capable of handling multinational traffic"; §6.2 "localized currency".
- **Problem:** no languages, address formats, units, phone formats or time zones are specified.
- **Decision:** **Assumption:** English only at launch, with i18n-ready code from M0: all strings translatable (gettext), Babel formatting for numbers/currency/dates, UTC storage with per-user time zone, E.164 phones, per-country address rules and area units, English full-text configuration.
- **Affects:** NFR-UX-07.1, NFR-UX-07.2, NFR-SCAL-01.3.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-31).

<a id="gap-53"></a>
### GAP-53 — "Credit wallet setup" as a lister step

- **Type / severity:** DIAGRAM · Low
- **Diagram text (SRC-03):** lister journey "Post property listing" → "Credit wallet setup".
- **Problem:** implies a manual setup step and a lister-only wallet, whereas every user receives promo credits and may buy credits (SRS §3.3, §6).
- **Decision:** every user has exactly one `CreditWallet`, created automatically with no user step. The domain model creates it when the account becomes verified, in the same transaction as the promo grant; unverified users read balance 0 (CI-01).
- **Affects:** FR-CRED-07.1.
- **Status:** Proposed — awaiting stakeholder confirmation.

<a id="gap-54"></a>
### GAP-54 — Diagram's NGINX/WhiteNoise box and polling placement

- **Type / severity:** DIAGRAM · Low
- **Diagram text (SRC-03):** "NGINX — Conceptual Static/Media Content Server (Whitenoise conceptually)"; "Django ORM • Session State • Periodic HTTP Polling" drawn between the application and data layers; external services not connected to anything.
- **Problem:** two static-file strategies are mixed; polling is drawn in the wrong place; integrations have no owner.
- **Decision:** in AWS, CloudFront → ALB → Gunicorn on ECS Fargate; static files served by WhiteNoise (hashed, compressed) and cached at CloudFront; media served from S3 through CloudFront (origin access control), never by Django. Nginx only in local docker compose (optional sidecar). Polling is **browser → app** (HTMX). External services are called from the web and Celery worker tiers.
- **Status:** Proposed — awaiting stakeholder confirmation.

<a id="gap-55"></a>
### GAP-55 — "Credit transactions within 500 ms" when a purchase includes gateway time

- **Type / severity:** INFEAS · Medium
- **SRS text:** §8.1 "All property search queries and credit transactions must complete within 500ms".
- **Problem:** a purchase includes time on the gateway's hosted page and gateway processing, which we do not control.
- **Decision:** "credit transactions" covers our server-side processing: the Show Number reveal end to end; fulfilment from receipt of the gateway confirmation to commit; and checkout creation excluding the outbound gateway API round trip (tracked separately as a dependency metric). Each p95 ≤ 500 ms standard, ≤ 1,000 ms peak.
- **Deviation from SRS:** gateway-hosted and gateway-API time is excluded.
- **Affects:** NFR-PERF-01.3, NFR-PERF-01.4.
- **Status:** Proposed — awaiting stakeholder confirmation.

<a id="gap-56"></a>
### GAP-56 — "1,000 concurrent transactions per second"

- **Type / severity:** VAGUE · High
- **SRS text:** §8.2 "handling 1,000 concurrent transactions per second"; §1.0 "high transaction volumes from launch".
- **Problem:** the phrase mixes concurrency (requests in flight) with throughput (per second). It is not said whether it is launch load or a design ceiling. Combined with §5.5, it implies up to 1,000 receipt emails per second (about 86 million per day), which affects provider quotas and cost.
- **Decision:** interpreted as a **design ceiling of 1,000 successful debit transactions per second sustained** across distinct wallets (≥ 10 min in M4, 15 min in M7), plus a hot-wallet correctness test. Emails are queued in the outbox and drain at the provider quota; at the ceiling the email-latency target may degrade, but no email is lost. Launch sizing follows the traffic forecast.
- **Deviation from SRS (interpretation):** "concurrent … per second" read as throughput.
- **Affects:** NFR-PERF-02.1 … 02.3.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-09).

<a id="gap-57"></a>
### GAP-57 — Tax on credit purchases

- **Type / severity:** MISSING · High
- **SRS text:** none.
- **Problem:** many countries tax digital services sold to consumers (VAT, GST, sales tax). This decides whether prices are tax-inclusive, what receipts must show, and whether a tax service (for example Stripe Tax) is needed.
- **Decision:** **Assumption:** price-book amounts are tax-inclusive; receipts show tax lines only once Finance provides the rules; no tax engine in MVP. Go-live in a market needs Finance/legal sign-off.
- **Affects:** FR-PAY-02, FR-PAY-05.7.
- **Status:** Proposed — awaiting stakeholder confirmation. **Blocking for M5** (OQ-06).

<a id="gap-58"></a>
### GAP-58 — Launch markets, hosting region and data residency

- **Type / severity:** MISSING · High
- **SRS text:** §1.0 "multinational traffic"; §10.1 "horizontal scalability across global markets without major refactoring".
- **Problem:** no launch markets, hosting region or data-residency obligations are named. They drive currencies, address and phone formats, SMS sender registration, privacy law, gateways, geocoding terms and the AWS region.
- **Decision:** **Assumption:** one AWS region at launch, parameterised in Terraform; CloudFront for global edge delivery; multi-currency and i18n-ready code. Multi-region or residency-specific deployments are Post-MVP, triggered by a market requirement.
- **Affects:** NFR-SCAL-01.3, NFR-AVAIL-01, FR-PAY-02.4.
- **Status:** Proposed — awaiting stakeholder confirmation. **Blocking for M0** (OQ-33).

<a id="gap-59"></a>
### GAP-59 — "Lister notified of new lead"

- **Type / severity:** DIAGRAM · Medium
- **Diagram text (SRC-03):** "Lister notified of new lead"; "Notification Services (Lead alerts …)".
- **Problem:** under renter-pays a "lead" is a renter revealing the lister's number. Telling the lister who revealed it shares the renter's identity without consent; an anonymous ping adds little.
- **Decision:** no per-reveal lister notification in MVP; listers see reveal counts on the dashboard (FR-LIST-04.9). An anonymous daily digest is a Post-MVP option.
- **Affects:** FR-LEAD-01.2.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-17).

<a id="gap-60"></a>
### GAP-60 — Account closure, unused credits and unverified accounts

- **Type / severity:** MISSING · Medium
- **SRS text:** none.
- **Problem:** what happens to unused credits, listings and financial records when a user leaves, and to accounts that never verify?
- **Decision:** **Assumption:** deletion is a Support-handled request in MVP. Verified users are anonymised, not deleted (ledger, reveals and orders are retained without PII); their listings are archived and contact fields cleared. Unused credits are forfeited unless legal says otherwise. Never-verified accounts are deleted after 7 days.
- **Affects:** NFR-SEC-05.4.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-16).

<a id="gap-61"></a>
### GAP-61 — Public visibility of the exact address

- **Type / severity:** MISSING · Medium
- **SRS text:** §4.2 makes the address mandatory; nothing says whether it is public.
- **Problem:** owner-listed homes are often the owner's residence. Publishing the exact address next to photos is a safety risk, but renters need a location to search.
- **Decision:** the lister chooses `address_display`: `APPROXIMATE` (default: locality and city shown, map pin offset 150–300 m and drawn as a circle) or `EXACT`. Search uses the true point; displayed distances are rounded to 0.5 km.
- **Affects:** FR-LIST-02.1, FR-LIST-05.3.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-22).

<a id="gap-62"></a>
### GAP-62 — Staff MFA (the stray `mfa_enabled` field)

- **Type / severity:** MISSING · High
- **SRS text:** §6.1 (stray) "The Users table should include fields for … mfa_enabled status." No MFA requirement anywhere else.
- **Problem:** staff can view PII, change listings and request credit adjustments. Staff accounts are the most valuable target.
- **Decision:** MFA (allauth MFA: TOTP plus recovery codes) is **mandatory for all staff** before any ops-console access; WebAuthn for Superadmin/Finance later. `mfa_enabled` is derived from the user's authenticators. Opt-in MFA for ordinary users is Post-MVP.
- **Affects:** FR-AUTH-06.4, FR-OPS-01.1, FR-PAY-01.5.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-41).

<a id="gap-63"></a>
### GAP-63 — Who owns the listing's contact phone?

- **Type / severity:** MISSING · Medium
- **SRS text:** none beyond §4.2 "contact information (phone/email)".
- **Problem:** a lister could enter someone else's number: renters then pay for a wrong number and a third party gets harassed.
- **Decision:** the contact phone must be OTP-verified when it differs from the verified account phone, before publish; changing it later also requires OTP before it takes effect.
- **Affects:** FR-LIST-02.7, FR-LIST-04.2.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-25).

<a id="gap-64"></a>
### GAP-64 — Hard-coded business constants

- **Type / severity:** VAGUE · Low
- **SRS text:** §3.3 "10 complimentary credits"; §5.1–5.6 "2 credits"; §6.2 "e.g., 20 credits, 50 credits, 120 credits".
- **Problem:** the business will tune these. The cost shown must always equal the cost charged, and changes must never rewrite history.
- **Decision:** `CREDITS_REVEAL_COST = 2` and `CREDITS_SIGNUP_PROMO = 10` are settings read by both UI and services; `ContactReveal.credits_spent` snapshots the price; changes apply only to new transactions. Packages and prices live in the database.
- **Affects:** FR-CRED-01.3, FR-AUTH-04.1, FR-PAY-02.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-43).

<a id="gap-65"></a>
### GAP-65 — Contact details in titles, descriptions or photos

- **Type / severity:** MISSING · High
- **SRS text:** none.
- **Problem:** a lister who writes "call 98xxx…" in the description, or puts the number on a photo, lets renters bypass Show Number entirely. Under renter-pays, listers have every reason to do this (GAP-01).
- **Decision:** clear phone, email and URL patterns in the title and description are blocked (client and server); obfuscated patterns ("nine eight…") raise a moderation flag. Text inside photos is handled by reports and moderation in MVP; OCR is Post-MVP.
- **Affects:** FR-LIST-02.9.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-39).

<a id="gap-66"></a>
### GAP-66 — Reveal abuse and contact scraping

- **Type / severity:** MISSING · High
- **SRS text:** none.
- **Problem:** a script with purchased or farmed credits can reveal thousands of lister contacts and resell them, harming listers and the platform.
- **Decision:** per-user hourly and daily reveal limits (configurable; excess returns a clear 429 with no debit); velocity and multi-account fraud signals feed the ops console; WAF bot rules; wallets can be frozen during fraud review; contact values never appear in logs or analytics.
- **Affects:** FR-CRED-08.1 … 08.3, FR-OPS-04.1.
- **Status:** Proposed — awaiting stakeholder confirmation (OQ-35).

<a id="gap-67"></a>
### GAP-67 — Transaction history scope and filters

- **Type / severity:** VAGUE · Low
- **SRS text:** §6.5 "a detailed, filterable history of all credit purchases and consumption events".
- **Problem:** promo grants, adjustments and reversals are neither purchases nor consumption; hiding them would make the balance impossible for users to reconcile. "Filterable" by what is not said.
- **Decision:** history shows **every** ledger entry with a label and the balance after; filters by type (purchase, consumption, promo, adjustment/reversal) and date range; purchases show the payment method; consumption rows link to the property and its free contact view. 25 rows per page, newest first.
- **Affects:** FR-PAY-05.1 … 05.6.
- **Status:** Proposed — awaiting stakeholder confirmation.

<a id="gap-68"></a>
### GAP-68 — Toast notifications vs WCAG 2.1 AA

- **Type / severity:** CONTRA · Medium
- **SRS text:** §5.6 "non-disruptive, in-app notification (e.g., a toast or alert bar) … direct, high-contrast link to the Purchase Credits tab"; §11.1 "minimal, non-modal confirmation message (e.g., a toast notification)"; §12.0 "WCAG 2.1 Level AA".
- **Problem:** typical auto-dismissing toasts fail WCAG (2.2.1 Timing Adjustable) and are often not announced to screen readers (4.1.3 Status Messages). A toast that contains a link can disappear before a keyboard user reaches it.
- **Decision:** toasts are live regions (`role="status"`), stay at least 10 s, pause while hovered or focused, and can be dismissed by keyboard. The insufficient-credit toast (which contains an action link) stays until dismissed. The revealed contact itself is always shown inline, so the toast never carries information found nowhere else.
- **Affects:** FR-CRED-06.4, NFR-UX-02.1, NFR-A11Y-01.4.
- **Status:** Proposed — awaiting stakeholder confirmation.

<a id="gap-69"></a>
### GAP-69 — Modal vs non-modal presentation of the revealed contact

- **Type / severity:** CONTRA · Low
- **SRS text:** §5.4 "clearly presented in a confirmation modal or designated area"; §11.1 "display a minimal, non-modal confirmation message".
- **Problem:** a modal plus a toast is a double confirmation, and the modal adds focus-trap complexity on mobile.
- **Decision:** the contact replaces the Show Number button in a designated inline area (HTMX swap, focus moved to the contact), together with the non-modal toast. No modal in MVP.
- **Affects:** FR-CRED-04.1, NFR-UX-02.1.
- **Status:** Proposed — awaiting stakeholder confirmation.

---

## 3. Deviation register

Every place where the knowledge base knowingly departs from the SRS text, in one list. Each needs stakeholder confirmation.

| # | GAP | SRS § | SRS says | We do | Recorded in |
|---|---|---|---|---|---|
| D-01 | [02](#gap-02) | 6.1 | `last_login_date` column | Django `last_login` (naming only) | FR-PAY-01.5 |
| D-02 | [06](#gap-06) | 3.3 | Promo on first login after registration | Promo on first verified login / verification | FR-AUTH-04.1, architecture AR-5 |
| D-03 | [07](#gap-07) | 3.4 | JWT for session management | Server-side sessions; JWT only for a future API | FR-AUTH-05.4, ADR-0003, DEV-SEC-1 |
| D-04 | [08](#gap-08) | 8.2 | Serializable / optimistic locking / Kafka | READ COMMITTED + row lock + constraints | NFR-PERF-02.4, ADR-0005, DEV-SEC-3, P-01 |
| D-05 | [09](#gap-09) | 6.4 | Verified via webhook | Webhook or server-side gateway verification | FR-PAY-04.2 |
| D-06 | [10](#gap-10) | 5.5 | Email concurrently with deduction | Outbox, sent after commit | FR-CRED-05.3, ADR-0006 |
| D-07 | [15](#gap-15) | 10.2 | ≥ 90 % coverage | ≥ 90 % domain code, ≥ 85 % whole repo (ratchet) | NFR-CODE-01.3 |
| D-08 | [17](#gap-17) | 8.1 | All requests within 500/1000 ms | Server-side p95 | NFR-PERF-01.1 … 01.4 |
| D-09 | [39](#gap-39) | 4.4 | Metrics instantly | ≤ 60 s for counters | FR-LIST-04.10, listings design §10.3 |
| D-10 | [55](#gap-55) | 8.1 | Credit transactions within 500 ms | Our-side processing only | NFR-PERF-01.3 |
| D-11 | [13](#gap-13), [35](#gap-35), [38](#gap-38), [56](#gap-56) | 6.2, 5.1, 8.2 | (ambiguous wording) | Documented interpretations | Respective entries |
| PC-01 | [12](#gap-12) | 9.1 | (baseline: blind index for login email) | **Proposed change:** login email plaintext under storage encryption | ADR-0010, AR-4, DEV-SEC-5, OQ-DM-04 → OQ-29 |

Not deviations, but worth stating because readers may assume otherwise: Argon2id instead of bcrypt is **compliant** ("e.g., bcrypt"); a hash chain in PostgreSQL is **compliant** (one of the two options §9.2 lists).

---

## 4. Cross-document consistency items

Differences found between documents in `docs/` while writing this analysis. The authoritative document is named; the other is to be aligned in its next revision.

| ID | Item | Documents | Resolution |
|---|---|---|---|
| CI-01 | When is the wallet created? Catalog FR-CRED-07.1: "created automatically with the account". Domain model §6.1: "created when the account becomes verified (same transaction as the promo grant)". | 02 catalog vs design/01 | Domain model is authoritative. The catalog's acceptance intent (automatic, no setup step) is met either way. Align the FR-CRED-07.1 wording in catalog v0.2. |
| CI-02 | Ledger field names. Catalog: `process_info`, `hash`. Domain model: `server_process_id`, `request_id`, `app_release`, `entry_hash`. | 02 catalog vs design/01 | Domain model is the schema of record (GAP-33). The catalog uses descriptive names. |
| CI-03 | Aspect-ratio range. Development Approach §7.4: "3:4 to 2:1 (US-206)". Listings design §8.3 and catalog FR-LIST-02.12: accept 4:3–16:9, auto-crop near ratios, reject portrait and panoramas. US-206 is the tag story. | delivery/01 vs design/05, 02 | Listings design is authoritative. Correct delivery/01 §7.4. |
| CI-04 | Header balance refresh. Catalog NFR-UX-01.2: polling every 30 s while visible. Performance doc P-02 (proposed change): event-driven out-of-band updates plus refresh on tab focus, no global polling. | 02 catalog vs quality/02 | **Recommendation:** accept P-02. The SRS only asks for a prominent, persistent balance (§11.1); the user's own reveals and purchases update it immediately; other-device changes appear on focus. If accepted, the catalog acceptance criterion changes to "updated immediately after the user's own credit actions and on tab focus". |
| CI-05 | Login email protection (baseline blind index vs ADR-0010 proposed plaintext). | Team baseline vs architecture, design/01, quality/01 | Decision needed: OQ-29 (GAP-12). |
| CI-06 | Purchase allocation percentile: US-509 p95 vs architecture/catalog p99. | delivery/02 vs architecture, 02 | p99 ≤ 5 s (the stricter value; performance doc P-05). |
| CI-07 | Saving a property: catalog FR-SAVE-01.1 requires a verified account; search design OQ-SRCH-07 says "login only" is acceptable. | 02 vs design/06 | Baseline: verified (consistent with GAP-29). OQ-42. |
| CI-08 | Service naming (verb-first vs entity-first), queue names, CSP wording, HTMX polling trigger syntax. | architecture/03 CS-1 … CS-4, quality/02 P-04, delivery/03 | Engineering-internal; owned by the codebase-structure document. No requirements impact. |
| CI-09 | URL paths. The catalog uses older aliases (`/credits/buy/`, `/account/saved/`); the backlog uses `/account/transactions/`. The codebase URL map uses `/my/credits/buy/`, `/my/saved/`, `/my/credits/`, `/payments/return/<gateway>/<uuid>/`. | 02 catalog, delivery/02 vs architecture/03 §7, design/07 §5 | The codebase URL map owns routes (payments design "route harmonisation"). Paths in requirement acceptance criteria are indicative; align them in catalog v0.2. |

---

## 5. Confirmation process

1. The Product Owner reviews this document with the client stakeholders, starting with the **blocking** entries (GAP-01, 12, 57, 58) and their questions in [04 §1](04-open-questions.md#1-blocking-questions-at-a-glance).
2. Each answer is written to the [decision log](04-open-questions.md#5-decision-log) with date and approver. The entry's status here changes to *Accepted*, *Rejected* (with the replacement decision) or *Superseded*.
3. Rejected or changed decisions update the [catalog](02-requirements-catalog.md) (new requirement IDs; old ones marked *Withdrawn*, never reused) and the affected ADRs, in one PR.
4. An unanswered entry never stops work: we build on the documented decision and the delivery team escalates it as a risk when its needed-by milestone starts ([Development Approach §7.3](../delivery/01-development-approach.md)).
