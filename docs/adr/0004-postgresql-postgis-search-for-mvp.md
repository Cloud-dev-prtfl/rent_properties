# ADR-0004: PostgreSQL + PostGIS + pg_trgm search for the MVP (no Elasticsearch)

Decides the search engine for property discovery: PostgreSQL 17 itself, using PostGIS for geospatial filters, `pg_trgm` for fuzzy matching and built-in full-text search, served from a read replica with a Valkey result cache. A dedicated search cluster is deferred until measured triggers fire.

Status: Draft v0.1 (2026-10-21)

| | |
|---|---|
| Decision status | Proposed |
| Date | 2026-10-21 |
| Deciders | Tech Lead (owner); PO acknowledges |
| Consulted | Platform, Product (search UX) |
| Supersedes / superseded by | — |
| Requirements | SRS §4.5 ("search index must be optimized for fast, relevant results using geospatial queries, supporting advanced multi-selection filtering, sorting options (newest, price), and fuzzy search matching"), §8.1 (p95 < 500 ms standard, < 1,000 ms peak); FR-LIST-05, NFR-PERF-01 |
| Gap / open question | Known issue #17 (GAP-17); A-4 / OQ-PERF-01 (traffic forecast) |
| Related | [Search design 06](../design/06-search-and-discovery.md) (authoritative for indexes, queries, cache and triggers) · [01 §12, §13.2, §16](../architecture/01-system-architecture.md#12-caching-strategy) · [NFR §6, §7](../quality/02-nfr-performance-and-scalability.md#6-database-scaling) |

## Context and problem statement

Visitors search by location (text, place or radius), price range, property type and the AgentListed/OwnerListed tag, with multi-select filters, sorting by newest or price, and typo-tolerant keyword matching (SRS §4.5). Results must return within the SRS latency targets. The planning tiers expect about 20 k published listings at launch and about 500 k at the growth tier, with 50 searches/s standard and 250 searches/s peak at growth ([NFR §4](../quality/02-nfr-performance-and-scalability.md#4-capacity-model-and-sizing-assumptions)).

The SRS says "search index", which is often read as "a search engine such as Elasticsearch". A separate engine adds a cluster, an indexing pipeline, eventual consistency between the database and the index, and a second place where listing data (but never contact data) lives.

**Question:** is PostgreSQL sufficient for MVP search at the required speed and relevance, or do we need a dedicated search engine from day one?

## Decision drivers

1. **Latency:** p95 ≤ 500 ms (standard) and ≤ 1,000 ms (peak) server-side for search (SRS §8.1).
2. **Required capabilities:** radius and location queries, multi-select filters, sorting, fuzzy and keyword matching (SRS §4.5).
3. **Freshness and correctness:** a rented, unlisted or suspended listing must disappear from results quickly (05 AC-LST-09) and must never be shown with stale status.
4. **Operational load and cost** for a small team.
5. **A clean upgrade path** if the catalogue or product needs outgrow PostgreSQL.

## Considered options

1. **PostgreSQL 17 + PostGIS + pg_trgm + full-text search** on a read replica, with a Valkey result cache.
2. **Amazon OpenSearch Service** (or self-managed Elasticsearch) fed from the database.
3. **Typesense or Meilisearch** (self-hosted or cloud).
4. **Algolia** (hosted search SaaS).

## Decision outcome

**Chosen option 1**, because at the expected catalogue sizes, well-chosen partial indexes make every canonical query an index scan within the latency budget, while avoiding a second data store, an indexing pipeline and index/DB inconsistency. The `SearchBackend` interface keeps a later move to OpenSearch a contained change.

Decision details (authoritative specification in [search design 06 §6–§9](../design/06-search-and-discovery.md#6-schema-indexes-and-search-vector)):

| Concern | Approach |
|---|---|
| Geospatial | PostGIS `geography` point (SRID 4326) on `Property.location`; `ST_DWithin` for radius; GiST partial index. A separate fuzzed `display_location` protects exact addresses where required |
| Keyword | Stored generated `search_vector` (title A, locality/city B, description C) with a GIN partial index; `websearch_to_tsquery` |
| Fuzzy | `pg_trgm` GIN index on normalised title (and on the place index for suggestions) as a fallback when full-text returns fewer than 5 results on page 1 (typos such as "balcny"), using the indexable `%>` operator only |
| Filters and sort | Partial B-tree indexes `WHERE status = 'PUBLISHED'`, leading with `country` and `city_normalized`, ordered for "newest" and "price"; keyset-friendly ordering with `id` as tie-breaker; low-cardinality filters (type, tag, bedrooms) applied after a selective scan |
| Place resolution | `search_place` materialised view for location suggestions, with geocoding as a fallback |
| Reads | `core.db.read_alias()` routes search to the replica; falls back to the primary if replica lag exceeds 5 s ([01 §13.2](../architecture/01-system-architecture.md#132-read-replica-routing-explicit-not-global)) |
| Cache | Ordered result IDs cached in Valkey, keyed by a per-country generation and the canonical query fingerprint; 60 s TTL with jitter (the search design's refinement of 01 §12); hydration by primary key **re-checks `status = PUBLISHED`**, so a stale cache can only miss a new listing, never show a removed one |
| Guards | Per-query `statement_timeout` (800 ms, with a 1,500 ms connection cap on the replica alias); page size and page number caps; bounded counts |
| Abstraction | `search.selectors.search_properties()` is the only entry point and delegates to a `SearchBackend` (`PostgresSearchBackend` now) |

### Consequences

- **Positive:**
  - One system of record; results are always consistent with listing status (no index lag).
  - No search cluster to size, patch, secure or pay for; replicas scale reads.
  - Contact data can never leak into a search index, because there is none.
  - Transactional, migration-managed indexes (`AddIndexConcurrently`) fit the normal deploy process.
- **Negative:**
  - Relevance tuning is more limited than in a dedicated engine (no learning-to-rank, limited per-language analysers, no native faceted counts at scale). *Mitigation:* the MVP needs filter-and-sort more than relevance ranking; English full-text only at launch; multilingual is post-MVP (US-910).
  - Search load competes with transactional load if it ever runs on the primary. *Mitigation:* replica routing and the cache; primary fallback only during replica problems, protected by statement timeouts.
  - Partial-index matching depends on the literal `status = 'PUBLISHED'` reaching the planner. *Mitigation:* client-side parameter binding for the replica alias; the nightly `EXPLAIN` guard alerts on sequential scans.
- **Neutral:** OpenSearch remains the documented next step, with a migration plan (indexer from `listing.*` outbox events, shadow mode, per-market cut-over behind a flag; [06 §14](../design/06-search-and-discovery.md#14-opensearch-migration-path)).

### Confirmation

- M3 exit (US-312): PT-01/PT-02 on the 500 k-listing `seed_perf` dataset meet p95 ≤ 500 ms at standard load and ≤ 1,000 ms at peak.
- Nightly `EXPLAIN` of the canonical queries shows index scans only.
- Production SLO on search latency with alerting ([NFR §2](../quality/02-nfr-performance-and-scalability.md#2-nfr-targets)).
- Cache hit ratio is monitored per market (`search_cache_hit_ratio`).

## Pros and cons of the options

### 1. PostgreSQL + PostGIS + pg_trgm + FTS (chosen)

- Good, because geo, text, fuzzy and filters combine in one query with one consistent snapshot.
- Good, because there is nothing extra to operate.
- Bad, because ranking sophistication and very large catalogues eventually favour a search engine.

### 2. Amazon OpenSearch Service

- Good, because of rich relevance tuning, analysers, aggregations and horizontal scale.
- Bad, because it adds a cluster (Multi-AZ, at least three nodes for production resilience), an indexing pipeline and backfills, and eventual consistency that must be guarded on every read.
- Bad, because its cost and operational load are not justified by the MVP catalogue size.

### 3. Typesense or Meilisearch

- Good, because they are fast, typo-tolerant and simple to start with.
- Bad, because they are another stateful service to run, and combining geo radius, numeric ranges and multi-select filters with our consistency guards still needs the same sync pipeline.

### 4. Algolia

- Good, because it is fully managed with excellent typo tolerance.
- Bad, because of per-request pricing at marketplace query volumes, data leaving our AWS account (residency, A-1), and the same synchronisation issues.

## Deviations from the SRS

None. The SRS asks for an optimised "search index"; PostgreSQL's GIN, GiST and B-tree indexes are that index. The interpretation is recorded so stakeholders do not expect a separate search product.

## Follow-ups

| # | Action | Owner | Milestone |
|---|---|---|---|
| 1 | Index set and generated column (verify the generated-column migration SQL) | Backend | M3 (US-301) |
| 2 | `seed_perf` dataset and PT-01/PT-02 | QA | M3 (US-312) |
| 3 | Harmonise 01 §12 with the per-country generation and 60 s TTL from the search design | Architecture | M3 |

## More information

- Triggers for moving to OpenSearch (any one, sustained): search p95 > 400 ms at standard load after tuning; replica CPU dominated by search; > 2 M published listings in one market or > 5 M overall; product needs PostgreSQL serves poorly ([06 §14.1](../design/06-search-and-discovery.md#141-triggers-any-one-sustained)). Such a move requires a new ADR with the evidence (US-908).
