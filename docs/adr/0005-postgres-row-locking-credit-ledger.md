# ADR-0005: PostgreSQL row-locking credit ledger (no Kafka)

Decides how credit balances change safely under concurrency: one short PostgreSQL transaction at READ COMMITTED that locks the user's wallet row, appends a hash-chained entry to an append-only ledger, and relies on database constraints as the last line of defence. No Kafka, no serializable isolation, no optimistic retry loops.

Status: Draft v0.1 (2026-10-21)

| | |
|---|---|
| Decision status | Proposed (to be confirmed with evidence by the M0 spike US-012 and the M4 load test PT-03) |
| Date | 2026-10-21 |
| Deciders | Tech Lead (owner); Finance and PO acknowledge the SRS deviation |
| Consulted | Security, QA (performance), Platform |
| Supersedes / superseded by | — |
| Requirements | SRS §3.3 (one-time promo, logged), §5.2 (atomic check, no negative balance), §5.3 (immutable ledger with transaction ID, balance before/after, timestamp, property ID, server process ID), §6.4 (purchase allocation), §8.2 (1,000 concurrent transactions/s), §9.2 (dedicated ledger or cryptographically linked audit trail, regular balance-vs-ledger audits with alerts); FR-CRED-02, FR-CRED-03, FR-CRED-07, NFR-PERF-02, NFR-SEC-02 |
| Gap / open question | GAP-08 (known issue #8), known issue #11 (hash chain), GAP-01 / OQ-01 (future lister-pays model) |
| Related | [01 §8.2, §11, §13.3](../architecture/01-system-architecture.md#82-sequence-show-number-sync-debit-async-email) · [03 §12 worked example](../architecture/03-codebase-structure.md#12-layering-rules-in-practice-worked-example-show-number) · [Domain model §6](../design/01-domain-model.md#6-credits) · [Credit wallet and ledger design](../design/02-credit-wallet-and-ledger.md) · [Engineering standards §8.2](../delivery/03-engineering-standards.md#82-why-read-committed-is-enough-for-the-debit) · [NFR §6](../quality/02-nfr-performance-and-scalability.md#6-database-scaling) |

## Context and problem statement

"Show Number" must check that the user has at least 2 credits and deduct them **atomically**, "immediately prior to the transaction to prevent any potential negative balances" (SRS §5.2), then display the contact immediately (§5.4). Every movement must be recorded in an immutable ledger with full audit metadata (§5.3), protected against manipulation by a dedicated ledger service or a cryptographically linked audit trail, and audited regularly against the live balance (§9.2). The mechanism must handle 1,000 concurrent credit transactions per second without inconsistency (§8.2). The SRS suggests "serializable, optimistic locking, or a resilient, queue-based processing system (like Apache Kafka)".

The only shared mutable state in a debit is **one wallet row** per user. Contention exists only between requests from the same user (double-clicks, parallel tabs, scripts); 1,000 debits per second normally come from 1,000 different wallets.

**Question:** which concurrency and integrity mechanism gives correct, auditable, immediate debits at 1,000/s with the least complexity?

## Decision drivers

1. **Correctness:** never a negative balance, never a double charge, exactly one ledger entry per movement (SRS §5.2–5.3).
2. **Synchronous result:** the user sees the number in the same request (SRS §5.4); latency p95 ≤ 500 ms (§8.1).
3. **Throughput:** ≥ 1,000 debits/s sustained across distinct wallets (§8.2).
4. **Tamper evidence and auditability** (§9.2), including against privileged insiders.
5. **Operational simplicity** for a small team ([ADR-0001](0001-django-modular-monolith.md)).
6. **Extensibility:** the same mechanism must later support other consumption models (lister-pays lead unlock, FR-CRED-07.4) without a schema change.

## Considered options

1. **PostgreSQL READ COMMITTED + pessimistic row lock on the wallet** (`SELECT … FOR UPDATE`), append-only hash-chained ledger, constraints and triggers.
2. **PostgreSQL SERIALIZABLE** with automatic retry on serialization failure.
3. **Optimistic locking** (version column, compare-and-set, retry on conflict).
4. **Kafka (or another log) as the source of truth**, with single-writer consumers per wallet partition and an asynchronous result.
5. **Valkey/Redis atomic counters (Lua)** with asynchronous persistence to PostgreSQL.
6. **A dedicated ledger database** (for example TigerBeetle) next to PostgreSQL. (Amazon QLDB, an earlier candidate, reached end of support in July 2025.)

## Decision outcome

**Chosen option 1**, because a row lock on the single row that carries the invariant makes "check then debit" atomic with no retries, keeps the reveal record, the ledger entry and the outbox message in one ACID transaction, and scales with the number of distinct wallets rather than with a global lock.

### The debit transaction (canonical form)

`SELECT … FOR UPDATE` on the wallet row is the canonical form, because the hash chain needs the wallet's current `head_seq` and `head_hash` read under the same lock that protects the balance. (The conditional `UPDATE … WHERE balance >= :cost RETURNING …` used in the M0 spike takes the same row lock and is equally correct for a plain balance; with the hash chain it needs a second update of the row, so it is not the default.)

```sql
BEGIN;                                                    -- READ COMMITTED (PostgreSQL default)
SET LOCAL lock_timeout = '2s';                            -- hot-wallet contention fails fast, no charge
SELECT id, balance, head_seq, head_hash, status
  FROM credits_creditwallet WHERE user_id = :user_id FOR UPDATE;   -- serialises writers on THIS wallet only
SELECT id FROM credits_creditledgerentry WHERE idempotency_key = :key; -- duplicate request? return the entry, no charge
-- service checks: status = 'ACTIVE' and balance >= :cost, else InsufficientCreditsError (rollback)
INSERT INTO credits_creditledgerentry
  (wallet_id, seq, entry_type, amount, balance_before, balance_after, reference_type, reference_id,
   idempotency_key, server_process_id, request_id, app_release, prev_hash, entry_hash, created_at, ...)
  VALUES (:w, :head_seq + 1, 'CONTACT_REVEAL', -:cost, :balance, :balance - :cost, 'listings.property', :property_public_id,
   :key, :proc, :req, :release, :head_hash, :entry_hash, :now, ...);
UPDATE credits_creditwallet
   SET balance = balance - :cost, head_seq = head_seq + 1, head_hash = :entry_hash
 WHERE id = :w;                                           -- HOT update: no indexed column changes
INSERT INTO leads_contactreveal (...);                    -- UNIQUE (user_id, property_id)
INSERT INTO core_outboxmessage (topic, payload, dedupe_key, ...);   -- receipt email after commit (ADR-0006)
COMMIT;
```

The Python shape is in [03 §12.2–12.4](../architecture/03-codebase-structure.md#122-lower-layer-service-creditsservicesdebit_credits).

### Why READ COMMITTED is sufficient

- A second transaction for the same wallet **waits** on the row lock. When the first commits, PostgreSQL re-evaluates the locked row and returns the **latest committed version** to the waiter, so the waiter checks the reduced balance. Each later statement in the waiter's transaction takes a fresh snapshot, so its idempotency check sees the first transaction's ledger entry.
- The invariant `balance >= 0` lives on one row, which the lock fully protects. Cross-row invariants are enforced by unique constraints, not by isolation: one reveal per `(user, property)`, one `SIGNUP_PROMO` per wallet, one `PURCHASE` per `(gateway, gateway_payment_id)`, a unique `idempotency_key` per ledger entry.
- SERIALIZABLE protects against anomalies (write skew over predicates) that cannot occur in this access pattern, at the cost of serialization failures and retry loops.

### Integrity controls

| Layer | Control |
|---|---|
| Constraints | `CHECK (balance >= 0)` on the wallet; `CHECK (balance_after = balance_before + amount)`, sign-by-type check, `UNIQUE (wallet_id, seq)`, unique `idempotency_key` on the ledger ([domain model §6.2](../design/01-domain-model.md#62-creditscreditledgerentry-append-only)) |
| Append-only | Trigger rejects `UPDATE`/`DELETE`/`TRUNCATE` on the ledger for every role; the runtime role `rpl_app` has no such privileges anyway ([04 §7.4](../architecture/04-infrastructure-and-deployment.md#74-database-bootstrap-infrasqlbootstrapsql)); contiguous `seq` enforced on insert; a deferred constraint trigger keeps the wallet head consistent with the ledger |
| Hash chain | Per-wallet SHA-256 chain: each entry stores `prev_hash` (the wallet's `head_hash` before insert) and `entry_hash` over a canonical serialisation of its fields; `hash_version` allows evolution ([credits design §5](../design/02-credit-wallet-and-ledger.md#5-hash-chain-specification)) |
| Audit | Nightly `audit_wallets`: balance = sum of entries, `head_seq`/`head_hash` match the last entry, chain recomputed from the last checkpoint. Any discrepancy → `LedgerAuditDiscrepancy`, wallet `FROZEN (AUDIT_MISMATCH)`, `ledger_audit_mismatches_total` pages on-call (SEV1) |
| Anchoring | Daily manifest of chain heads to an S3 Object Lock bucket in a separate AWS account, so even a database superuser cannot rewrite history undetected ([security §4.3](../quality/01-security-and-compliance.md#43-ledger-anchoring-addition)) |
| Forged appends | Nightly cross-check: every `PURCHASE` maps to a fulfilled, gateway-reconciled `PaymentOrder`; every `ADMIN_ADJUSTMENT` maps to an approved maker-checker request |
| Audit metadata (SRS §5.3) | Entry `public_id` (transaction ID), `balance_before`/`balance_after`, `created_at`, reference to the property, `server_process_id` (`<service>:<task-id>:<pid>`), `request_id`, `app_release` |

### Rules for every credit movement

| Rule | Detail |
|---|---|
| Single writer | Only `credits.services` (`debit_credits`, `grant_credits`, `grant_signup_promo`, `adjust_credits`, `reverse_entry`) write wallets or ledger entries (rule R3) |
| Generic API | Callers pass `entry_type`, `amount`, a `reference` (type + public ID) and an `idempotency_key`. A future `LEAD_UNLOCK` (lister-pays) is a new entry type and a new caller, not a schema change (FR-CRED-07.4) |
| Lock order | The wallet lock is always the **last** lock taken in a transaction (for example `PaymentOrder` row, then wallet). This prevents deadlocks between fulfilment, adjustments and reveals |
| Short transactions | No network I/O inside; `lock_timeout` 2 s on debit and fulfilment; side effects after commit through the outbox |
| Integers only | Credits are integers; money is integer minor units + ISO 4217, stored in `payments`, never in the ledger |

### Consequences

- **Positive:**
  - Correct by construction under concurrency, and provably so (constraints make a negative balance or a double charge impossible even with a code bug).
  - Synchronous: the contact is shown in the same request.
  - No new infrastructure; the ledger is in the same database as the data it references, so joins and audits are simple SQL.
  - Throughput scales with distinct wallets; the expected cost is about 6 statements and 2–5 ms per debit ([01 §13.3](../architecture/01-system-architecture.md#133-capacity-model-for-the-1000-debitss-design-point-to-be-validated-in-the-load-test)).
- **Negative:**
  - All credit writes go to one primary database; the ceiling is its commit rate (WAL and fsync, plus the synchronous Multi-AZ standby). *Mitigation:* vertical scaling, measured headroom from PT-03, connection pooling ladder, and the extraction seam to a dedicated ledger engine if sustained load ever far exceeds 1,000/s ([01 §16](../architecture/01-system-architecture.md#16-future-extraction-seams)).
  - A single wallet serialises at about 200–400 debits/s. *Mitigation:* irrelevant for a human user; per-user rate limits (10/min) and `lock_timeout` stop scripted abuse ([NFR §6.4](../quality/02-nfr-performance-and-scalability.md#64-hot-wallet-behaviour)).
  - The ledger table grows forever. *Mitigation:* insert-only tuning, BRIN index on `created_at`, monthly partitioning beyond about 100 M rows (its own ADR).
- **Neutral:** the hash chain detects edits and deletions, not well-formed forged appends; those are covered by the reconciliation cross-checks above.

### Confirmation

- **M0 spike (US-012):** k6 at 1,000 req/s for 5 minutes on dev-sized RDS: error rate < 0.1 %, 0 negative balances, ledger sum = balance; hot-wallet test with 200 concurrent requests gives exactly ⌊balance / 2⌋ successes. Results appended to this ADR.
- **Concurrency tests** in CI (`apps/credits/tests/test_concurrency.py`, thread harness with real commits; [testing §7](../delivery/04-testing-strategy.md#7-concurrency-tests-for-credit-debit)) and Hypothesis property tests on ledger invariants.
- **M4 (PT-03) and M7 (US-702):** ≥ 1,000 debits/s for 10 and 15 minutes, p95 within the SRS targets, all post-run invariants hold ([NFR §9.5](../quality/02-nfr-performance-and-scalability.md#95-post-run-invariants-all-must-hold)).
- In production: nightly audit clean; `ledger_audit_mismatches_total` stays at 0.

## Pros and cons of the options

### 1. READ COMMITTED + wallet row lock (chosen)

- Good, because the check and the debit are atomic with no retry logic.
- Good, because the reveal, ledger entry and outbox message commit together.
- Good, because contention is limited to one user's own concurrent requests.
- Bad, because write throughput is bounded by one primary (far above the requirement, to be proven by PT-03).

### 2. SERIALIZABLE

- Good, because the database detects every anomaly.
- Bad, because transactions fail with serialization errors under load and must be retried, which adds latency variance and code paths that are hard to test; it adds nothing for a single-row invariant.

### 3. Optimistic locking

- Good, because no locks are held while the application computes.
- Bad, because conflicts cause retries exactly when the same wallet is hit concurrently (double-clicks), and the hash-chain head must still be updated consistently; a pessimistic lock held for a few milliseconds is simpler and more predictable.

### 4. Kafka as the source of truth

- Good, because of very high throughput and an event log by design.
- Bad, because the result is asynchronous: the web request would have to wait for a consumer's reply (request-reply over a log) to show the number "immediately", which adds latency and failure modes.
- Bad, because PostgreSQL is still needed for the reveal record and history, so every debit becomes a dual write across two systems, and a second system of record must be operated and secured.
- Bad, because it solves a throughput problem we don't have at 1,000/s.

### 5. Valkey/Redis atomic counters

- Good, because Lua scripts are atomic and extremely fast.
- Bad, because the balance would live outside the ACID transaction that records the reveal; a crash between the two creates charges without reveals or the reverse. Cache memory is not an acceptable home for money-like state.

### 6. Dedicated ledger database

- Good, because purpose-built ledgers offer strong double-entry guarantees at very high throughput.
- Bad, because it is another stateful system with a dual-write boundary to PostgreSQL, a small operational ecosystem on AWS, and a capability far beyond the requirement. Kept as a future extraction target only.

## Deviations from the SRS

**Deviation from SRS §8.2:** the SRS suggests serializable isolation, optimistic locking or a queue such as Kafka. We use READ COMMITTED with a pessimistic row lock, database constraints and unique keys. It meets the same goal (no race conditions, no inconsistency at 1,000/s) more simply and with a synchronous result, and it is proven by load tests rather than assumed. Recorded as GAP-08, DEV-SEC-3 and NFR-PERF-02.4.

**Interpretation of SRS §9.2:** "dedicated financial ledger service *or* an immutable, cryptographically-linked audit trail". We implement the second: an append-only ledger with a per-wallet SHA-256 hash chain, nightly audits and external WORM anchoring.

## Follow-ups

| # | Action | Owner | Milestone |
|---|---|---|---|
| 1 | Run the US-012 spike; append the numbers and graphs to this ADR | Tech Lead | M0 |
| 2 | Ledger triggers, grants and hash chain; nightly audit job | Backend | M4 (US-401–US-404) |
| 3 | PT-03 at prod-size profile; decide RDS class and pooling (separate ADR if a pooler is needed) | QA + Platform | M4 (US-414) |
| 4 | Ledger anchoring to Object Lock | Platform | M4 (SEC-15) |

## More information

- Revisit if sustained credit-transaction load approaches the measured ceiling of the largest practical RDS class, or if many independent consumers need the ledger as an event stream (then publish ledger events through the outbox, keeping PostgreSQL as the source of truth).
