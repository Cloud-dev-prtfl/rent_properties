"""US-012 concurrency spike: can PostgreSQL row locking carry the credit debit path?

Throwaway prototype (kept as a benchmark). Uses its own `spike_*` tables, never app tables.
Two variants from the design docs:
  conditional — UPDATE … SET balance = balance - 2 WHERE id = $1 AND balance >= 2 RETURNING …
  lock        — SELECT … FOR NO KEY UPDATE, check, UPDATE (the variant design/02 §7.2 adopts,
                because the hash chain needs balance + head under one lock)
Each debit also appends a ledger row in the same transaction.

Usage (inside the dev container):
  python tests/load/spike_debit.py --dsn postgresql://rpl:rpl@db:5432/rpl --seconds 15 --threads 64
"""

import argparse
import random
import statistics
import threading
import time
from collections.abc import Callable

import psycopg

COST = 2

SCHEMA = """
DROP TABLE IF EXISTS spike_ledger, spike_wallet;
CREATE TABLE spike_wallet (
    id bigint PRIMARY KEY,
    balance integer NOT NULL CONSTRAINT ck_spike_balance_non_negative CHECK (balance >= 0)
);
CREATE TABLE spike_ledger (
    id bigserial PRIMARY KEY,
    wallet_id bigint NOT NULL REFERENCES spike_wallet (id),
    amount integer NOT NULL,
    balance_after integer NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ON spike_ledger (wallet_id);
"""


def debit_conditional(conn: psycopg.Connection, wallet_id: int) -> bool:
    with conn.transaction():
        row = conn.execute(
            "UPDATE spike_wallet SET balance = balance - %s "
            "WHERE id = %s AND balance >= %s RETURNING balance",
            (COST, wallet_id, COST),
        ).fetchone()
        if row is None:
            return False
        conn.execute(
            "INSERT INTO spike_ledger (wallet_id, amount, balance_after) VALUES (%s, %s, %s)",
            (wallet_id, -COST, row[0]),
        )
        return True


def debit_lock(conn: psycopg.Connection, wallet_id: int) -> bool:
    with conn.transaction():
        (balance,) = conn.execute(
            "SELECT balance FROM spike_wallet WHERE id = %s FOR NO KEY UPDATE", (wallet_id,)
        ).fetchone()
        if balance < COST:
            return False
        conn.execute(
            "UPDATE spike_wallet SET balance = %s WHERE id = %s", (balance - COST, wallet_id)
        )
        conn.execute(
            "INSERT INTO spike_ledger (wallet_id, amount, balance_after) VALUES (%s, %s, %s)",
            (wallet_id, -COST, balance - COST),
        )
        return True


VARIANTS: dict[str, Callable[[psycopg.Connection, int], bool]] = {
    "conditional": debit_conditional,
    "lock": debit_lock,
}


def reset(dsn: str, wallets: int, balance: int) -> None:
    with psycopg.connect(dsn, autocommit=True) as conn:
        conn.execute(SCHEMA)
        conn.execute(
            "INSERT INTO spike_wallet (id, balance) SELECT g, %s FROM generate_series(1, %s) g",
            (balance, wallets),
        )


def check_invariants(dsn: str, initial: int) -> dict[str, int]:
    with psycopg.connect(dsn) as conn:
        negative = conn.execute("SELECT count(*) FROM spike_wallet WHERE balance < 0").fetchone()[0]
        mismatched = conn.execute(
            """SELECT count(*) FROM spike_wallet w
               LEFT JOIN (SELECT wallet_id, sum(amount) s FROM spike_ledger GROUP BY wallet_id) l
                 ON l.wallet_id = w.id
               WHERE w.balance <> %s + coalesce(l.s, 0)""",
            (initial,),
        ).fetchone()[0]
        entries = conn.execute("SELECT count(*) FROM spike_ledger").fetchone()[0]
    return {
        "negative_balances": negative,
        "ledger_mismatches": mismatched,
        "ledger_entries": entries,
    }


def hot_wallet(dsn: str, variant: str, balance: int, concurrency: int) -> None:
    """Many concurrent debits on ONE wallet: exactly floor(balance / COST) may succeed."""
    reset(dsn, wallets=1, balance=balance)
    debit = VARIANTS[variant]
    # Keep concurrency below the server's max_connections (100 locally; higher on RDS).
    successes, barrier = [], threading.Barrier(concurrency, timeout=30)

    def worker() -> None:
        with psycopg.connect(dsn) as conn:
            barrier.wait()
            if debit(conn, 1):
                successes.append(1)

    threads = [threading.Thread(target=worker) for _ in range(concurrency)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    expected = balance // COST
    inv = check_invariants(dsn, balance)
    ok = len(successes) == expected and inv["negative_balances"] == 0
    ok = ok and inv["ledger_mismatches"] == 0
    print(
        f"[hot-wallet/{variant}] {concurrency} concurrent debits, balance {balance}: "
        f"{len(successes)} succeeded (expected {expected}), invariants {inv} -> "
        f"{'PASS' if ok else 'FAIL'}"
    )


def throughput(dsn: str, variant: str, wallets: int, threads: int, seconds: float) -> None:
    initial = 1_000_000
    reset(dsn, wallets=wallets, balance=initial)
    debit = VARIANTS[variant]
    latencies: list[list[float]] = [[] for _ in range(threads)]
    stop = time.monotonic() + seconds

    def worker(slot: int) -> None:
        rng = random.Random(slot)  # noqa: S311 — load generation, not security
        with psycopg.connect(dsn) as conn:
            while time.monotonic() < stop:
                t0 = time.perf_counter()
                debit(conn, rng.randint(1, wallets))
                latencies[slot].append(time.perf_counter() - t0)

    pool = [threading.Thread(target=worker, args=(i,)) for i in range(threads)]
    started = time.monotonic()
    for t in pool:
        t.start()
    for t in pool:
        t.join()
    elapsed = time.monotonic() - started
    samples = sorted(x for lat in latencies for x in lat)
    q = statistics.quantiles(samples, n=100)
    inv = check_invariants(dsn, initial)
    ok = inv["negative_balances"] == 0 and inv["ledger_mismatches"] == 0
    print(
        f"[throughput/{variant}] {threads} connections, {wallets} wallets, {elapsed:.1f}s: "
        f"{len(samples) / elapsed:,.0f} debits/s | p50 {q[49] * 1000:.1f} ms, "
        f"p95 {q[94] * 1000:.1f} ms, p99 {q[98] * 1000:.1f} ms | invariants {inv} -> "
        f"{'PASS' if ok else 'FAIL'}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dsn", required=True)
    parser.add_argument("--seconds", type=float, default=15)
    parser.add_argument("--threads", type=int, default=64)
    parser.add_argument("--wallets", type=int, default=10_000)
    parser.add_argument("--hot-concurrency", type=int, default=80)
    args = parser.parse_args()
    for variant in VARIANTS:
        hot_wallet(args.dsn, variant, balance=100, concurrency=args.hot_concurrency)
        throughput(args.dsn, variant, args.wallets, args.threads, args.seconds)
    with psycopg.connect(args.dsn, autocommit=True) as conn:
        conn.execute("DROP TABLE IF EXISTS spike_ledger, spike_wallet")


if __name__ == "__main__":
    main()
