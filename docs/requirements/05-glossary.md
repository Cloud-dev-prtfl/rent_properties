# Glossary

Purpose: one meaning for every domain term, so that the SRS, the diagrams, the documents in `docs/`, the code and the UI use the same words. Where the sources use a different word, §1 maps it to the project term.

Status: Draft v0.1 (2026-10-21)

Related: [01 Source Documents](01-source-documents.md) · [02 Requirements Catalog](02-requirements-catalog.md) · [03 Gap Analysis & Decisions](03-gap-analysis-and-decisions.md) · [04 Open Questions](04-open-questions.md) · [Domain Model](../design/01-domain-model.md)

---

## 1. Source terms mapped to project terms

| Source term | Where it appears | Project term | Canonical code name |
|---|---|---|---|
| Credit Count | SRS §5.1 | Credit balance | `credits.CreditWallet.balance` |
| Show Number | SRS §5.1, §11.1 | Show Number (UI label); contact reveal (domain action) | `leads.services.reveal_contact` |
| Lead | SRS §1.0, §5.5; SRC-03 "LEAD created" | Contact reveal (MVP). An inquiry-style lead is Post-MVP | `leads.ContactReveal` |
| "Lister wants to unlock lead?", "Lead unlocked" | SRC-03 flow chart | Lead unlock (lister-pays), Post-MVP | Reserved entry type `LEAD_UNLOCK` |
| Lister (agents/owners) | SRS §1.0 | Lister | Any verified `accounts.User` who owns a `listings.Property` |
| Renter, Seeker, Website visitor | SRS §1.0, §4.5; SRC-03 "Renter / Seeker Portal" | Renter (logged in) or visitor (anonymous) | `accounts.User` / anonymous session |
| AgentListed, OwnerListed | SRS §4.3 | Lister tag | `Property.lister_tag` = `AGENT_LISTED` \| `OWNER_LISTED` |
| Property, Property listing, PropertyListing | SRS §4; SRC-03 ORM box | Listing (UI), Property (code) | `listings.Property` |
| My Properties | SRS §4.4, §7.2 | My Properties dashboard | `/my/properties/` |
| Purchase Credits | SRS §6.1, §7.2 | Purchase Credits page | `/my/credits/buy/` (the catalog's older alias `/credits/buy/` resolves here) |
| Profile Icon Dropdown | SRS §7.1 | Profile dropdown | Header component |
| Transaction | SRS §5.3, §6.5; SRC-03 ORM box | Ledger entry (credit movement) or payment order (money movement) | `credits.CreditLedgerEntry`, `payments.PaymentOrder` |
| Transaction ID | SRS §5.3 | Ledger entry public ID | `CreditLedgerEntry.public_id` (UUID) |
| Immutable ledger, cryptographically-linked audit trail | SRS §5.3, §9.2 | Credit ledger with hash chain | `credits.CreditLedgerEntry` |
| Server process ID | SRS §5.3 | Server process identity | `server_process_id`, `request_id`, `app_release` |
| Credit wallet, owner wallet dashboard | SRC-03 | Wallet; credit balance and transaction history page | `credits.CreditWallet`; `/my/credits/` |
| "Credit wallet setup" | SRC-03 flow chart | No equivalent: wallets are automatic (GAP-53) | — |
| Ops Console | SRC-03 | Ops console | `/ops/` (hardened admin + `apps.moderation` views) |
| Verification API, KYC Docs, Ownership Proofs | SRC-03 | Owner verification (Post-MVP) | `apps.verification` |
| Notification Services (lead alerts, OTP delivery) | SRC-03 | Notifications | `apps.notifications`; Twilio Verify for OTP |
| Periodic HTTP Polling | SRC-03 | HTMX polling | `hx-trigger="every Ns"` pattern |
| Hot search results | SRC-03 cache box | Search result cache | `apps.search` cache in Valkey |
| Promo / complimentary credits | SRS §3.3 | Welcome credits (UI); signup promo (domain) | Ledger entry type `SIGNUP_PROMO` |
| Credit packages | SRS §6.2 | Credit package | `payments.CreditPackage` |
| Localized currency pricing | SRS §6.2 | Price book | `payments.CreditPackagePrice` |
| Mark as rented, unlist | SRS §4.4 | Listing status transitions | `RENTED`, `UNLISTED` |

---

## 2. Domain glossary

| Term | Definition | Code / reference |
|---|---|---|
| **Account (unverified / verified)** | A registered user. *Unverified* until email confirmation or phone OTP succeeds; unverified accounts can browse but cannot transact (GAP-29). *Verified* accounts can rent and list. | `User.status`: `UNVERIFIED`, `ACTIVE`, `SUSPENDED`, `DELETED` |
| **Address display** | Lister's choice of how much of the address is public: `APPROXIMATE` (locality and city, offset pin; default) or `EXACT`. Search always uses the true location. | `Property.address_display` (GAP-61) |
| **Admin adjustment** | A staff-initiated credit correction, recorded as a new ledger entry after four-eyes approval. Balances are never edited directly. | `ADMIN_ADJUSTMENT`, `credits.CreditAdjustmentRequest` |
| **Anchor (ledger anchor)** | A periodic root hash over all wallet chain heads, written to write-once (WORM) S3 storage, so that tampering by privileged database users is detectable. | `credits.LedgerAnchor` |
| **Append-only** | A table whose rows can be inserted and read but never updated or deleted, enforced by database triggers and role privileges. Applies to the ledger and the audit log. | `CreditLedgerEntry`, `core.AuditLog` |
| **Audit log** | Append-only record of security-relevant and staff actions (who, what, when, before/after), separate from the credit ledger. | `core.AuditLog` |
| **Balance** | The number of credits in a wallet. An integer, never negative (`CHECK (balance >= 0)`). Always equals the sum of the wallet's ledger amounts. | `CreditWallet.balance` |
| **Blind index** | A keyed hash (HMAC-SHA256) of a normalised value, stored next to an encrypted field so that equality lookups (for example "is this phone already verified?") work without decrypting. | `phone_hmac`, `contact_phone_hmac`, `email_hmac` |
| **Cooldown** | Waiting period before an action may be repeated, for example 14 days after a rejected tag-change request, or 60 s between OTP resends. | — |
| **Contact (listing contact)** | The name, phone (required) and email (optional) that a renter gets by revealing a listing. Stored per listing, encrypted, never sent to a browser before a reveal (GAP-20). | `Property.contact_name`, `contact_phone`, `contact_email` |
| **Contact reveal** | The paid act of showing a listing's contact to one user, and the record of it. One per (user, property); later views are free. In MVP this is what "lead" means. | `leads.ContactReveal`, `leads.services.reveal_contact` |
| **Contact snapshot** | Encrypted copy of the contact as it was at reveal time, kept on the reveal for the receipt and history (24 months). | `ContactReveal.contact_*_snapshot` (GAP-34) |
| **Credit** | The platform's internal unit of value. Integer only. Bought in packages or granted as promo; spent on reveals (2 per reveal in MVP). Credits are not money and never expire in MVP (OQ-12). | — |
| **Credit package** | A purchasable bundle of credits (for example 20, 50, 120). | `payments.CreditPackage` |
| **Debit** | A ledger entry that reduces a balance. Executed only through the credits service with an atomic conditional update. | `credits.services.debit_credits` |
| **Deviation from SRS** | A documented, justified decision to do something other than the SRS text. Listed in the deviation register. | [03 §3](03-gap-analysis-and-decisions.md#3-deviation-register) |
| **Derived requirement** | A requirement not stated in the SRS but needed because of a gap decision, a diagram element or another requirement. Always labelled "Derived". | [02 §0.2](02-requirements-catalog.md#02-column-meanings) |
| **Draft** | A listing that has not been submitted. Saved server-side from creation; lenient validation; archived after 90 idle days. | `Property.status = DRAFT` |
| **Entry type** | The category of a ledger entry; decides its sign and meaning. | §3.1 |
| **Expiry (listing)** | A published listing that is not renewed within 60 days leaves search and becomes `EXPIRED`; one click renews it. | GAP-45 |
| **Four-eyes approval (maker-checker)** | A sensitive change needs a requester and a different approver. Used for credit adjustments. | `CreditAdjustmentRequest` |
| **Frozen wallet** | A wallet whose user-initiated debits are blocked (fraud review, audit mismatch, chargeback). Grants and reversals are still possible. | `CreditWallet.status = FROZEN` |
| **Fulfilment** | Granting purchased credits for a confirmed payment: order → `FULFILLED` and a `PURCHASE` ledger entry, in one transaction, exactly once. | `payments.services.fulfill_order` |
| **Gateway (payment gateway)** | An external payment provider behind the `PaymentGateway` interface: Stripe Checkout, PayPal Orders v2, optionally Razorpay. | `payments/gateways/` |
| **Gateway-verified confirmation** | Proof of payment obtained server-to-server: a signature-verified webhook or a server-side API check (retrieve or capture). The only trigger for fulfilment (GAP-09). | — |
| **Genesis hash** | The fixed starting `prev_hash` of a new wallet's hash chain. | `CreditWallet.head_hash` |
| **Geocoding** | Converting a typed address into coordinates (a PostGIS point, SRID 4326) through a provider adapter. | `geo.GeocodingService` |
| **GeoIP** | Estimating a visitor's country from their IP address (MaxMind GeoLite2), used only as a fallback for currency selection. | — |
| **Hash chain** | Each ledger entry stores the previous entry's hash and its own `entry_hash = SHA-256(prev_hash ‖ canonical(entry))`, so any change to history breaks verification. One chain per wallet. | `prev_hash`, `entry_hash` |
| **Hot wallet** | A wallet receiving many concurrent debits at once (for example a scripted user). Used in correctness tests: concurrency must never overdraw it. | NFR-PERF-02.2 |
| **Idempotency key** | A unique key per intended operation, enforced by a unique constraint, so retries and duplicate events have no extra effect. Examples: `promo:signup:<user_public_id>`, `pay:<gateway>:<gateway_payment_id>`. | `CreditLedgerEntry.idempotency_key` |
| **Insufficient credit** | A reveal attempt with balance below the reveal cost. Nothing is deducted; a non-modal message links to Purchase Credits. | FR-CRED-06 |
| **Lead** | In MVP, a contact reveal. The flow chart's inquiry-style lead (free renter inquiry that a lister unlocks) is Post-MVP. | GAP-01 |
| **Lead unlock** | Post-MVP lister-pays model: a lister spends credits to see a renter's inquiry contact. | Reserved `LEAD_UNLOCK` |
| **Ledger (credit ledger)** | The append-only, hash-chained list of every credit movement. The source of truth for balances. | `credits.CreditLedgerEntry` |
| **Ledger audit** | Scheduled job that recomputes every balance from the ledger and verifies each hash chain; any discrepancy alerts on-call and freezes the wallet. | `LedgerAuditRun`, `LedgerAuditDiscrepancy` |
| **Lister** | A verified user acting as the owner or agent of a listing. Not a separate account type. | GAP-04 |
| **Lister tag** | Mandatory, exclusive label on a listing: AgentListed or OwnerListed. Immutable after first publish except through a tag-change request. | `Property.lister_tag` |
| **Listing** | A property offered for rent, with status, attributes, photos and contact. | `listings.Property` |
| **Market** | A launch country with its currency, address rules and price book. Searches are scoped to one market. | OQ-33 |
| **Minor units** | Money stored as an integer in the currency's smallest unit (cents, paise; 0 decimals for JPY, 3 for KWD) together with an ISO-4217 code. Floats are never used for money. | `amount_minor`, `currency` |
| **Moderation case** | A unit of work in the moderation queue, opened by a report, an automated flag or a fraud signal. | `moderation.ModerationCase` |
| **Monthly-equivalent rent** | Rent converted to a monthly figure (weekly × 52 / 12) for filtering and sorting. | `Property.rent_monthly_minor` |
| **Ops console** | Staff interface: hardened Django admin plus custom views for moderation, tag review, fraud, ledger audit, jobs and support. MFA required. | `/ops/` |
| **Outbox (transactional outbox)** | A table row written in the same transaction as a business change and dispatched after commit by a worker. Guarantees side effects (emails, cache bumps) happen only for committed changes, at least once. | `core.OutboxMessage` |
| **Payment order** | Our record of one purchase attempt, with a snapshot of package, credits, amount and currency, and the gateway references. | `payments.PaymentOrder` |
| **Price book** | The per-currency price list for credit packages, with validity periods, maintained by Finance. No live FX conversion. | `payments.CreditPackagePrice` |
| **Pre-moderation** | Review before publishing. In MVP only for listings flagged by automated checks (`flagged_only`). | `LISTINGS_PREMODERATION_MODE` |
| **Presigned upload** | The browser uploads a photo directly to S3 using a short-lived signed policy (size and type limits), so image bytes never pass through the web servers. | Listings design §8.2 |
| **Promo credits (signup promo)** | 10 credits granted once, when an account first becomes verified; one per verified identity. Shown to users as "Welcome credits". | `SIGNUP_PROMO`, `credits.SignupPromoClaim` |
| **Property type** | Controlled list: Apartment, Studio, House, Townhouse, Villa, Room, Shared accommodation. | `PropertyType` |
| **Pseudonymisation** | Replacing direct identifiers with non-identifying ones (UUIDs, HMACs) in logs, analytics and payloads. | NFR-SEC-01.5 |
| **Reconciliation** | Scheduled comparison of gateway records, payment orders and ledger entries; re-verifies stuck orders and alerts on mismatches. | FR-PAY-04.6 |
| **Relist / renew** | Returning a rented, unlisted or expired listing to `PUBLISHED`; publish checks run again. | FR-LIST-04.4 |
| **Renter** | A user (or anonymous visitor) searching for a property. Revealing contacts requires a verified account with credits. | GAP-04 |
| **Reveal cost** | Credits charged per reveal: 2 in MVP, read from one setting and snapshotted on each reveal. | `CREDITS_REVEAL_COST`, `ContactReveal.credits_spent` |
| **Reversal** | A ledger entry that cancels all or part of an earlier entry (refunds, chargebacks, corrections). Never pushes a balance below 0. | `REVERSAL`, `credits.services.reverse_entry` |
| **Saved property** | A renter's bookmark of a listing; feeds the listing's "saves" metric. | `listings.SavedProperty` |
| **Show Number** | The UI action (button) that triggers a paid contact reveal. Label shows the cost: "Show Number · 2 credits". | FR-CRED-01 |
| **Show Number click** | Metric: every click on Show Number by a logged-in non-owner, including insufficient-credit outcomes. Differs from "reveals". | GAP-40 |
| **Staff** | Platform employees using the ops console, in groups Moderator, Support, Finance, Superadmin. MFA mandatory. | GAP-04, GAP-62 |
| **Tag-change request** | A lister's request to switch the lister tag after publishing; decided by a Moderator. | `listings.PropertyTagChangeRequest` |
| **Transaction history** | The user's list of all ledger entries (purchases, reveals, promo, adjustments, reversals) with filters and free contact re-views. | FR-PAY-05 |
| **Variant (image variant)** | A resized, metadata-stripped copy of an uploaded photo for a specific use: `thumb`, `card`, `md`, `lg`, `og`, `email`. | `PropertyImage` |
| **View (listing view)** | Metric: a detail-page render by a non-owner, non-bot viewer, deduplicated per viewer per 30 minutes. | GAP-40 |
| **Wallet (credit wallet)** | The single credit account of a user, created automatically when the account is verified; holds the balance and the hash-chain head. | `credits.CreditWallet` |
| **Webhook** | An HTTP callback from a gateway or provider. Signature-verified, stored once per event ID, processed idempotently. | `payments.PaymentWebhookEvent` |

---

## 3. Enumerations

### 3.1 Ledger entry types

| Type | Sign | Created by | Meaning |
|---|---|---|---|
| `SIGNUP_PROMO` | + | System, at first verification | 10 welcome credits, once per verified identity |
| `PURCHASE` | + | Payment fulfilment | Credits from a paid package |
| `CONTACT_REVEAL` | − | `reveal_contact` | Credits spent on a Show Number reveal (references the property) |
| `ADMIN_ADJUSTMENT` | ± | Staff, four-eyes | Goodwill, corrections, bad-reveal refunds |
| `REVERSAL` | ± | Refund/dispute webhook or staff | Cancels an earlier entry; capped so the balance never goes below 0 |
| `LEAD_UNLOCK` | − | — | Reserved for the Post-MVP lister-pays model |

### 3.2 Listing statuses

| Status | Public? | Meaning |
|---|---|---|
| `DRAFT` | No | Being written |
| `PENDING_REVIEW` | No | Submitted and held for moderation |
| `PUBLISHED` | Yes | Live in search; Show Number available |
| `REJECTED` | No | Refused by a Moderator; can be edited and resubmitted |
| `RENTED` | No ("No longer available") | Marked rented by the lister |
| `UNLISTED` | No | Withdrawn by the lister (or by repeated "already rented" reports) |
| `EXPIRED` | No | Not renewed within 60 days |
| `SUSPENDED` | No | Taken down by a Moderator |
| `ARCHIVED` | No | Deleted by the lister or archived by the system; kept for reveals and ledger references |

### 3.3 Other enumerations

| Enumeration | Values | Defined in |
|---|---|---|
| Lister tag | `AGENT_LISTED`, `OWNER_LISTED` | Listings design §2.1 |
| User status | `UNVERIFIED`, `ACTIVE`, `SUSPENDED`, `DELETED` | Domain model §12.6 |
| Payment order status | `CREATED`, `PENDING`, `FULFILLED`, `FAILED`, `CANCELLED`, `EXPIRED`, `NEEDS_REVIEW`, `REFUNDED`, `DISPUTED` | Domain model §12.4 |
| Tag-change request status | `PENDING`, `APPROVED`, `REJECTED`, `CANCELLED` | Domain model §12.3 |
| Staff groups | Moderator, Support, Finance, Superadmin | GAP-04 |
| Wallet status | `ACTIVE`, `FROZEN` | Domain model §6.1 |

---

## 4. Abbreviations

| Abbreviation | Meaning |
|---|---|
| ADR | Architecture Decision Record |
| ALB | AWS Application Load Balancer |
| ASVS | OWASP Application Security Verification Standard |
| CDN | Content delivery network (CloudFront) |
| CSP | Content Security Policy |
| DPDP | India's Digital Personal Data Protection Act, 2023 |
| DPO | Data Protection Officer |
| DR | Disaster recovery |
| DSR | Data-subject request (access, export, deletion) |
| E.164 | International phone-number format (`+<country><number>`) |
| FTS | Full-text search (PostgreSQL `tsvector`) |
| FX | Foreign exchange (currency conversion) |
| GDPR | EU General Data Protection Regulation |
| HLRD | High Level Requirements Document (SRC-02) |
| IaC | Infrastructure as Code (Terraform) |
| ISO 4217 | Three-letter currency codes (`USD`, `INR`, …) |
| KMS | AWS Key Management Service |
| KYC | Know Your Customer (identity verification) |
| MFA | Multi-factor authentication |
| MoSCoW | Must / Should / Could / Won't prioritisation |
| MVP | Minimum viable product (milestones M0–M7) |
| OTP | One-time passcode |
| p95 / p99 | 95th / 99th percentile latency |
| PCI DSS, SAQ A | Payment Card Industry Data Security Standard; the self-assessment for merchants that fully outsource card handling |
| PII | Personally identifiable information |
| PITR | Point-in-time recovery |
| RBAC | Role-based access control |
| RPO / RTO | Recovery point objective (max data loss) / recovery time objective (max downtime) |
| RUM | Real-user monitoring |
| SLA / SLO | Service-level agreement / objective |
| SRID 4326 | WGS 84 latitude/longitude coordinate system |
| SRS | Software Requirements Specification (SRC-01, the authoritative source) |
| SSO | Single sign-on (Google, Apple) |
| TPS | Transactions per second |
| WAF | Web application firewall |
| WCAG | Web Content Accessibility Guidelines (2.1 AA required) |
| WORM | Write once, read many (S3 Object Lock) |
