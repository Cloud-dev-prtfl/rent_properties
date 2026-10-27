# Load tests

| Script | Purpose | When |
|---|---|---|
| `spike_debit.py` | US-012 concurrency spike: hot-wallet correctness + throughput of the debit design | Locally (indicative) and on dev RDS (authoritative) |
| `reveal_debit.js` (M4) | k6: Show Number at 1,000 req/s for 10 min (NFR-PERF-02) | Milestone exits on staging |
| `search.js` (M3) | k6: search p95 < 500 ms | Milestone exits on staging |
