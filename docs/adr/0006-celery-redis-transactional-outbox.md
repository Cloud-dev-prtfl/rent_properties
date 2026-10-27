# ADR-0006: Celery + Valkey background jobs with a transactional outbox

Decides how work leaves the request: Celery workers on a Valkey broker run all background jobs, and every side effect that must happen if and only if a business transaction commits goes through a PostgreSQL outbox table written in that same transaction.

Status: Draft v0.1 (2026-10-21)

| | |
|---|---|
| Decision status | Proposed (confirmed by the M0 outbox tests in US-005/US-007 and the M4 broker-failover drill) |
| Date | 2026-10-21 |
| Deciders | Tech Lead (owner); PO acknowledges the SRS deviation |
| Consulted | Platform, QA, Security |
| Supersedes / superseded by | — |
| Requirements | SRS §5.5 (email "concurrently" with the deduction, via a reliable, monitored service), §4.2 (automatic thumbnails), §6.3–6.4 (webhook-driven status updates, reconciliation), §9.2 (regular audits), §8.3 (runbooks); FR-CRED-05.3, FR-CRED-05.5, FR-NOTIF-01, FR-PAY-04.6, NFR-AVAIL-01.8 |
| Gap / open question | [GAP-10](../requirements/03-gap-analysis-and-decisions.md#gap-10) (known issue #10); CS-2 (queue split, [03 §16](../architecture/03-codebase-structure.md#16-open-questions-and-consistency-items)); NFR proposal P-04 (`critical` queue) |
| Related | [01 §5, §9](../architecture/01-system-architecture.md#9-synchronous-vs-asynchronous-paths) · [03 §5, §10](../architecture/03-codebase-structure.md#10-celery-tasks-layout-and-routing) · [Domain model §2.1, §12.8](../design/01-domain-model.md#21-coreoutboxmessage) · [Notifications design §4–5](../design/08-notifications.md#4-architecture) · [04 §6.1, §8.5, §13.4](../architecture/04-infrastructure-and-deployment.md#61-cluster-and-services) · [ADR-0005](0005-postgres-row-locking-credit-ledger.md) |

## Context and problem statement

The SRS asks for an automated receipt email "concurrently with the credit deduction" (§5.5), sent through a "highly reliable, monitored transactional email service". Much other work must not run inside a web request either: image verification and thumbnails (§4.2), payment reconciliation (§6.4), nightly ledger audits (§9.2), analytics flushes, retention purges and periodic schedules.

The difficulty is the boundary between the database transaction and everything outside it:

| Approach | Failure |
|---|---|
| Send the email (or enqueue the task) **inside** the transaction | The transaction can still roll back (insufficient credits, lock timeout, constraint violation). The user gets a receipt for a debit that never happened. |
| Enqueue **after** commit with `transaction.on_commit` only | If the process dies between `COMMIT` and the enqueue, or the broker loses the message (failover, eviction, flush), the receipt is lost and nothing records that it was owed. |

Constraints: the web tier is stateless; the debit path has a p95 budget of 500 ms (§8.1); at the design point 1,000 debits/s each produce one message (§8.2); no network I/O is allowed inside `transaction.atomic()` (rule R7, [01 §10](../architecture/01-system-architecture.md#10-modular-monolith-boundary-rules)); the team is small.

**Question:** which job system do we use, and how do we guarantee that a side effect happens exactly when its business transaction commits, without ever losing it?

## Decision drivers

1. **Never act on rolled-back state.** No receipt for a debit that did not commit (SRS §5.5, FR-CRED-05.3).
2. **Never lose a committed side effect.** At-least-once delivery that survives broker loss and process crashes.
3. **Exactly-once effect where it matters**, through idempotent consumers (one receipt per reveal, FR-CRED-05.5).
4. **Request latency.** Nothing slow or remote on the request path (SRS §8.1).
5. **Throughput** of about 1,000 messages/s at the design point without hurting the debit transaction.
6. **Operability.** Visible backlog, retries, dead letters and a retry button in the ops console (the diagram's "monitor & manage jobs"); one periodic scheduler.
7. **Simplicity and ecosystem.** OpenTelemetry and Sentry integrations, local parity, a tool the team already knows.

## Considered options

**Job execution**

1. **A1. Celery 5 + Valkey (Redis protocol) broker + django-celery-beat**
2. **A2.** Celery with Amazon SQS as the broker
3. **A3.** Celery with RabbitMQ (Amazon MQ)
4. **A4.** A PostgreSQL-backed job queue (for example Procrastinate)
5. **A5.** Django's tasks framework (`django.tasks`, Django 6.0+; the `django-tasks` backport on 5.2)
6. **A6.** RQ, Dramatiq or Huey

**Delivery guarantee for side effects**

1. **B1. Transactional outbox:** an `OutboxMessage` row written in the business transaction, relayed after commit (fast path) with a periodic sweeper (safety net)
2. **B2.** `transaction.on_commit` enqueue only
3. **B3.** Enqueue or send inside the transaction (dual write)
4. **B4.** Change data capture (Debezium or logical replication) from the outbox or domain tables

## Decision outcome

**Chosen: A1 + B1.** Celery is the mature default for Django, with retries, routing, beat scheduling and first-class OpenTelemetry/Sentry support. The outbox makes the commit itself the record of the side effect, so the broker becomes a delivery accelerator rather than a store of truth. A PostgreSQL queue (A4) would give transactional enqueue for free, but it would put polling load and media-job churn on the primary that already carries the 1,000 debits/s money path. CDC (B4) gives the same guarantee as B1 with far more infrastructure.

### Rule: every asynchronous job is recoverable from PostgreSQL

| Kind of work | Mechanism | If the broker loses the message |
|---|---|---|
| Side effects of a business transaction that must not be lost: receipt emails, `payment.*` events, account and listing notifications | `core.outbox.publish()` **inside** the transaction; relay after commit | The `PENDING` outbox row is re-dispatched by the sweeper within about 30 s |
| Work whose pending state already lives in a domain row: image processing (`PropertyImage.status = PROCESSING`), geocode retry (`geocode_status = PENDING`), `payments.verify_order` (order `PENDING`) | `transaction.on_commit(lambda: task.delay(id))` | The owning app's sweeper re-enqueues it (images: 15 min; payments: reconciliation every 5 min) |
| Periodic jobs (audits, reconciliation, flushes, purges) | celery-beat with `DatabaseScheduler` | The next tick runs it; every periodic job is idempotent and catches up |
| Best-effort work that is harmless to lose (search-cache generation bump, view counters) | Synchronous Valkey call in `on_commit` | Nothing; TTLs bound the staleness ([01 §12](../architecture/01-system-architecture.md#12-caching-strategy)) |

**Forbidden:** calling `.delay()`/`apply_async()` inside `transaction.atomic()` (option B3), and any task that is the *only* record of work still owed.

### Publishing

```python
# apps/core/outbox.py (illustrative)
def publish(*, topic: str, payload: dict, dedupe_key: str | None = None,
            available_at: datetime | None = None) -> OutboxMessage:
    if not transaction.get_connection().in_atomic_block:
        raise OutboxOutsideTransaction(topic)          # an outbox row outside a transaction is a bug
    _assert_ids_only(payload)                           # public IDs and codes; no PII, no contact details
    fields = {"topic": topic, "payload": payload, "available_at": available_at or timezone.now()}
    if dedupe_key:                                      # UNIQUE dedupe_key makes publishing idempotent
        msg, created = OutboxMessage.objects.get_or_create(dedupe_key=dedupe_key, defaults=fields)
    else:
        msg, created = OutboxMessage.objects.create(**fields), True
    if created and msg.available_at <= timezone.now():
        transaction.on_commit(lambda: relay_outbox_message.delay(msg.id))   # fast path, after commit only
    return msg
```

The schema is in the [domain model §2.1](../design/01-domain-model.md#21-coreoutboxmessage) (`topic`, `payload`, `dedupe_key`, `status` `PENDING`/`DISPATCHED`/`DEAD`, `attempts`, `available_at`, `last_error`, partial index on `available_at WHERE status = 'PENDING'`). Topics are singular domain nouns (`contact.revealed`, `payment.succeeded`, `listing.published`); the registry is in the [notifications design §4.2](../design/08-notifications.md#42-topic-registry). Subscribers register in their app's `ready()` with `core.outbox.register_handler(topic, handler)`, so lower layers never import higher ones (rule R1).

### Relaying: claim, process, settle

The relay never holds a row lock while a handler does network I/O. Handlers call email providers with timeouts of up to 10 s, and the runtime role has `idle_in_transaction_session_timeout = 10s` ([04 §7.4](../architecture/04-infrastructure-and-deployment.md#74-database-bootstrap-infrasqlbootstrapsql)). The relay therefore takes a **lease** in a short transaction, works outside any transaction, then settles in a second short transaction.

```sql
-- 1. Claim (own short transaction, no I/O). No row returned = taken by someone else, not due, or done: no-op.
UPDATE core_outboxmessage
   SET attempts = attempts + 1,
       available_at = now() + interval '5 minutes'          -- lease: expires if this worker dies
 WHERE id = (SELECT id FROM core_outboxmessage
              WHERE id = :id AND status = 'PENDING' AND available_at <= now()
              FOR UPDATE SKIP LOCKED)
RETURNING id, public_id, topic, payload, attempts;
COMMIT;

-- 2. Run every handler registered for the topic, outside any transaction.
--    Handlers are idempotent on the message public_id (e.g. NotificationLog UNIQUE (outbox id, channel)).

-- 3. Settle (own short transaction)
UPDATE core_outboxmessage SET status = 'DISPATCHED', dispatched_at = now() WHERE id = :id;          -- all handlers OK
UPDATE core_outboxmessage SET available_at = now() + :backoff, last_error = :scrubbed WHERE id = :id;  -- retryable
UPDATE core_outboxmessage SET status = 'DEAD', last_error = :scrubbed WHERE id = :id;                -- exhausted/permanent
```

| Rule | Value |
|---|---|
| Lease | 5 minutes; longer than the relay task's `time_limit` (90 s) |
| Retry backoff | 30 s, 1 min, 5 min, 15 min, 30 min, 1 h, 2 h, 4 h, 6 h, 10 h (±10 % jitter), then `DEAD` (10 attempts, about 24 h) ([notifications §5.2](../design/08-notifications.md#52-errors-retries-and-dead-letter)) |
| Delays | Expressed through `available_at`, **never** through Celery `countdown`/`eta` (see the visibility timeout below) |
| Multiple subscribers | The message is `DISPATCHED` only when every handler succeeded; handlers that already succeeded are no-ops on retry |
| Ordering | Not guaranteed across messages. Handlers read current state through selectors ("fetch before act") and never trust a payload snapshot |
| Sweeper | `core.sweep_outbox`, beat every 30 s on `maintenance`: enqueues the relay for up to 1,000 due `PENDING` rows with `available_at <= now() - interval '10 seconds'` (the grace period lets the fast path win). Duplicates are no-ops because of the claim |
| Dead letter | `DEAD` rows are kept; `/ops/jobs/` lists them and a Superadmin can retry one or a filtered batch (resets `attempts` and `available_at`). A `DEAD` `contact.revealed`, `payment.*` or `account.password_*` message pages on-call |
| Retention | `DISPATCHED` rows hard-deleted after 14 days (daily job); `DEAD` kept until handled |

**Consistency note:** the [notifications design §4.1](../design/08-notifications.md#41-flow) sequence shows `SELECT … FOR UPDATE SKIP LOCKED` followed by the send. Read it as the claim, process, settle sequence above; no lock is held during the send.

### Celery configuration invariants

| Setting | Value | Why |
|---|---|---|
| Broker | Dedicated ElastiCache for Valkey cluster, `maxmemory-policy noeviction`, `rediss://` with certificate verification and AUTH | A broker must never evict; the cache cluster is separate and uses LRU ([01 §5](../architecture/01-system-architecture.md#5-c4-level-2-containers)) |
| Serialisation | `task_serializer = "json"`, `accept_content = ["json"]` | No pickle; messages survive code changes across releases |
| Arguments | IDs and primitives only, never model instances or PII | Tasks re-read current state; nothing sensitive sits in the broker |
| Results | `task_ignore_result = True`, no result backend | State lives in domain tables |
| Acknowledgement | `task_acks_late = True`, `task_reject_on_worker_lost = True`, `worker_prefetch_multiplier = 1` | Every task is idempotent, so redelivery is safe and fair dispatch avoids starving queues |
| Visibility timeout | `broker_transport_options = {"visibility_timeout": 3600}` | With the Redis transport, an unacknowledged message from a crashed worker returns only after this timeout, and an `eta` beyond it causes duplicate delivery. Hence no long countdowns, and crash recovery comes from the PostgreSQL sweepers, not the broker |
| Time limits | Per task `soft_time_limit` and `time_limit` (relay 60 s / 90 s; image processing 60 s / 90 s) | No runaway tasks |
| Names | Explicit `@shared_task(name="app.verb_noun")` | Renames don't strand queued messages ([04 §8.5](../architecture/04-infrastructure-and-deployment.md#85-deploy-order-and-compatibility-rules)) |
| Routing | Declared once in `config/celery.py`; queues `default`, `maintenance` (ECS `worker`) and `media` (ECS `worker-media`) | [03 §10](../architecture/03-codebase-structure.md#10-celery-tasks-layout-and-routing). A `critical` queue is added only if metrics show money-path tasks waiting behind email (CS-2) |
| Beat | `django_celery_beat.schedulers:DatabaseScheduler`, exactly one ECS task (`minimumHealthyPercent 0`, `maximumPercent 100`), heartbeat alarm | Two beats would double-fire schedules |
| Worker flags | `--without-gossip --without-mingle`, `--max-tasks-per-child` | Less broker chatter; bounded memory growth |
| Tests | Real commits with `django_capture_on_commit_callbacks`; `task_always_eager` is never used to test the money path | Eager mode hides the commit boundary this ADR is about |

### Observability

`outbox_pending_count`, `outbox_oldest_pending_age_seconds` (measured on **due** rows, `available_at <= now()`, so scheduled retries don't count; warn above 5 min, page above 15 min, as in [notifications §15](../design/08-notifications.md#15-monitoring-and-alerting)), `outbox_dead_count` by topic, per-queue depth and oldest-message age (published every 30 s by `core.publish_queue_depth`, also the autoscaling signal for workers), task failure and retry counters, and OpenTelemetry Celery instrumentation that links the request trace to the task trace. Flower is not deployed in production; `/ops/jobs/` and CloudWatch cover job visibility ([01 §7](../architecture/01-system-architecture.md#7-mapping-the-clients-architecture-diagram-to-this-design)).

### Consequences

- **Positive:**
  - A receipt can only exist for a committed debit, and a committed debit always gets its receipt, even if the broker is flushed or fails over.
  - The broker holds no truth, so a Valkey failover is an availability blip, not a data-loss incident ([04 §13.4](../architecture/04-infrastructure-and-deployment.md#134-failure-modes)).
  - One uniform pattern for notifications, payment events and future integrations (for example an OpenSearch indexer or an event bus fed by outbox handlers, [01 §16](../architecture/01-system-architecture.md#16-future-extraction-seams)).
- **Negative:**
  - One extra insert in every publishing transaction (about +1 statement on the debit path), plus a later update and delete. *Mitigation:* measured in PT-03; the hot partial index only covers `PENDING` rows.
  - At the 1,000/s ceiling the table would receive about 86 M rows a day. *Mitigation:* per-table autovacuum tuning (`autovacuum_vacuum_scale_factor = 0.01`); if sustained volume exceeds about 5 M messages/day, a follow-up ADR moves to daily range partitions dropped after retention. That ADR must handle the fact that a unique `dedupe_key` across partitions needs the partition key in the constraint.
  - At-least-once means rare duplicates (for example a worker dying between the provider accepting an email and `SENT` being committed, [notifications §5.4](../design/08-notifications.md#54-delivery-semantics-and-known-duplicate-window)). *Mitigation:* idempotency keys and `NotificationLog`; a duplicate receipt is harmless, a missing one is not.
  - Two Valkey clusters to operate. *Mitigation:* small `cache.t4g` nodes; both managed.
  - The receipt email is asynchronous (p95 ≤ 60 s after commit) rather than "concurrent" (see Deviations).
- **Neutral:** Kafka is not needed ([ADR-0005](0005-postgres-row-locking-credit-ledger.md)). If many independent consumers appear, an outbox handler can publish to SNS/EventBridge or Kafka while PostgreSQL stays the source of truth.

### Confirmation

- **M0 (US-005, US-007):** tests prove that a rolled-back transaction leaves no message and no effect; a committed one produces exactly one handler effect even when the relay runs twice in parallel; a claim followed by a simulated worker death is re-dispatched after the lease.
- **CI:** a Semgrep rule (`celery-enqueue-in-atomic`) flags `.delay(`/`.apply_async(` inside `transaction.atomic()` in `apps/`; an architecture test asserts that every task in `config/celery.py` routing has an explicit name.
- **M4 broker-failover drill** on staging ([04 §13.6](../architecture/04-infrastructure-and-deployment.md#136-drills)): fail over and flush the broker during a reveal load; afterwards the count of `NotificationLog` receipts equals the count of `ContactReveal` rows.
- **M4 PT-03:** the outbox insert keeps the debit within p95 500 ms, and `outbox_oldest_pending_age_seconds` stays below 60 s at 1,000/s with the email sink adapter.
- **Production:** the outbox alarms above stay quiet; `DEAD` count is reviewed weekly.

## Pros and cons of the options

### A1. Celery + Valkey broker (chosen)

- Good, because it is the most widely used Django job system: retries, routing, beat, time limits, OTel and Sentry integrations.
- Good, because Valkey is already in the stack (cache, sessions) and has local parity in docker compose.
- Bad, because the Redis transport has sharp edges (visibility timeout, no durable delivery guarantees). Neutralised by the outbox and the domain sweepers.

### A2. Celery with SQS

- Good, because SQS is durable and fully managed.
- Bad, because of polling latency, weaker Celery feature support on that transport (no remote control or events), and poor local parity (needs an emulator). The outbox already provides durability.

### A3. Celery with RabbitMQ (Amazon MQ)

- Good, because AMQP acknowledgements and routing are the most faithful Celery transport.
- Bad, because it adds a third managed stateful service with its own cost and failover behaviour, for guarantees the outbox already gives us.

### A4. PostgreSQL-backed queue (for example Procrastinate)

- Good, because enqueueing inside the business transaction gives outbox semantics with no broker.
- Bad, because every queue poll, lock and state change lands on the primary that carries the money path, including high-churn media jobs; and its ecosystem (scheduling, monitoring, instrumentation) is smaller than Celery's.

### A5. Django tasks framework

- Good, because it is the future standard API in Django core.
- Bad, because Django 6.0 ships only development backends, Django 5.2 LTS needs the third-party backport, and a production backend would still need a worker. Re-evaluate at the Django 6.2 LTS upgrade (about April 2027).

### A6. RQ, Dramatiq or Huey

- Good, because they are simpler than Celery.
- Bad, because they have smaller ecosystems (scheduling, OTel, Sentry) and none removes the need for an outbox.

### B1. Transactional outbox (chosen)

- Good, because the message commits atomically with the business change, and recovery needs only PostgreSQL.
- Bad, because of the extra write and table maintenance described above.

### B2. `on_commit` only

- Good, because it is a one-liner with no extra table.
- Bad, because a crash or broker loss after commit silently drops the side effect, and nothing records that it was owed. Allowed only where a domain row already records the pending work (the rule table above).

### B3. Enqueue or send inside the transaction

- Bad, because it acts on state that may roll back (a receipt for an uncharged reveal), and it puts network I/O inside the transaction. Forbidden.

### B4. Change data capture

- Good, because no relay polling is needed and the database log is the source.
- Bad, because it needs logical replication slots on RDS, a Debezium/Kafka Connect deployment and slot-lag monitoring (an unconsumed slot can fill the primary's storage). Far beyond MVP needs.

## Deviations from the SRS

**Deviation from SRS §5.5:** "Concurrently with the credit deduction, the system MUST trigger an automated email." We trigger the email **after the deduction commits**, asynchronously, with a target of p95 ≤ 60 s from commit to provider acceptance (FR-CRED-05.3). Sending concurrently (before the outcome is known) would produce receipts for deductions that roll back, which defeats the email's purpose as "a purchase receipt". The user sees the contact immediately in the same request (§5.4), so the experience is unchanged. Recorded as GAP-10 / D-06. Where the address is unverified, the receipt is held and the toast says so ([notifications §5.3](../design/08-notifications.md#53-verified-address-rule-and-held-emails), GAP-37).

## Follow-ups

| # | Action | Owner | Milestone |
|---|---|---|---|
| 1 | `core.outbox` (publish, registry, claim/settle relay, sweeper), tests listed above | Backend | M0 (US-005) |
| 2 | `config/celery.py` with the invariants and routing; `core.publish_queue_depth` metric | Backend + Platform | M0 (US-007) |
| 3 | Semgrep rule `celery-enqueue-in-atomic` | Tech Lead | M0 (US-002) |
| 4 | `/ops/jobs/` outbox backlog and `DEAD` retry view | Backend | M6 (US-611) |
| 5 | Broker failover drill with receipt-count check | Platform + QA | M4 |
| 6 | Outbox volume review; partitioning ADR if sustained volume > 5 M/day | Tech Lead | M7, then quarterly |
| 7 | Align the notifications design §4.1 wording with claim, process, settle | Notifications owner | M1 |
| 8 | Re-evaluate the Django tasks framework | Tech Lead | Django 6.2 LTS upgrade |

## More information

- Revisit if: broker incidents become frequent; a third-party consumer needs a durable event stream (publish from outbox handlers to SNS/EventBridge or Kafka); or Django's tasks framework gains a mature production backend.
- Backlog mapping of queue names (US-007's six names onto three queues) is in [03 §10](../architecture/03-codebase-structure.md#10-celery-tasks-layout-and-routing).
