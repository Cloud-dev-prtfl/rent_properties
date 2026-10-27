# ADR-0013: Credit-debit concurrency spike results (US-012)

Records the evidence for ADR-0005 (PostgreSQL row locking instead of Kafka) and for the lock mode chosen in [design/02 §7.2](../design/02-credit-wallet-and-ledger.md).

Status: Draft v0.1 (2026-10-27): local run done; RDS run pending the `dev` environment

| | |
|---|---|
| Decision status | Accepted locally; to be confirmed on dev RDS |
| Date | 2026-10-27 |
| Deciders | Tech Lead |
| Consulted | Platform |
| Supersedes / superseded by | — |
| Requirements | SRS §8.2 (1,000 concurrent credit transactions/s, no inconsistency); NFR-PERF-02, NFR-SEC-02 |
| Gap / open question | Known issue #8 (no Kafka); OQ-09 (meaning of 1,000 TPS) |
| Related | [ADR-0005](0005-postgres-row-locking-credit-ledger.md), [`tests/load/spike_debit.py`](../../tests/load/spike_debit.py) |

## Context and problem statement

The SRS suggests serializable isolation, optimistic locking or Kafka for 1,000 debits/s. Our design keeps READ COMMITTED with a row lock on the wallet, plus a `CHECK (balance >= 0)` and an append-only ledger insert in the same transaction. Before building M4 on it, we must show that it is both **correct** under contention and **fast** enough.

## Method

`tests/load/spike_debit.py` creates throw-away `spike_wallet` / `spike_ledger` tables and tests two variants. Each debit is one transaction: a balance change plus a ledger insert.

- **conditional:** `UPDATE … SET balance = balance - 2 WHERE id = $1 AND balance >= 2 RETURNING balance`
- **lock:** `SELECT balance … FOR NO KEY UPDATE`, check, `UPDATE`. This is the adopted variant, because the hash chain needs the balance and the chain head read under one lock.

Two tests per variant:

1. **Hot wallet:** N concurrent debits released together by a barrier on one wallet with 100 credits. Exactly ⌊100 / 2⌋ = 50 must succeed.
2. **Throughput:** 48 client connections debit random wallets out of 10,000 for 15 s. Then invariants are checked: no negative balance, and for every wallet `balance = initial + Σ ledger.amount`.

## Results: local run (2026-10-27)

Environment: developer laptop, Docker Desktop (8 vCPU, 4 GB), PostgreSQL 17 + PostGIS 3.5 container with default settings. The Python load generator ran on the same machine, competing for the same CPUs.

| Test | conditional | lock (adopted) |
|---|---|---|
| Hot wallet, 80 concurrent debits | 50 succeeded (expected 50) | 50 succeeded (expected 50) |
| Throughput | **2,511 debits/s** | **1,965 debits/s** |
| Latency p50 / p95 / p99 | 18.4 / 29.7 / 36.8 ms | 23.4 / 36.8 / 48.5 ms |
| Negative balances | 0 | 0 |
| Ledger mismatches | 0 | 0 |

## Decision outcome

- **Correctness is confirmed** for both variants: exact success counts under contention, and zero inconsistencies over about 67,000 debits.
- **Throughput passes the target with about 2× headroom**, even on a laptop, using the adopted `FOR NO KEY UPDATE` variant. Kafka or a queue-based debit path is **not needed** (ADR-0005 stands).
- The lock variant costs about 20 % throughput versus the conditional `UPDATE`. That is acceptable for the hash-chain guarantee. If production measurements ever come close to the limit, the conditional variant remains a fallback, at the cost of a different chain design.

### Consequences

- **Positive:** M4 can build on the planned design without an architecture change.
- **Negative:** the numbers are indicative only. The load generator and database shared one machine, the Python client threads limit throughput, and the hot-wallet test used 80 rather than 200 connections because local `max_connections` is 100.

### Confirmation (pending)

Repeat on the `dev` stack (RDS sized like production, the client on a separate task, PgBouncer/RDS Proxy in front). The test uses 200 hot-wallet connections and k6 at 1,000 req/s for 5 minutes through the real HTTP endpoint (M4). Record the results here and change the status to Accepted.
