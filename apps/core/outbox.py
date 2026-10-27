"""Transactional outbox (ADR-0006).

`publish()` writes a row inside the caller's transaction and kicks a relay task after commit.
The relay uses claim → process → settle with a lease, so no row lock is held while a handler
talks to an external provider. Handlers must be idempotent: a message can be delivered more
than once, and its `public_id` is the consumer's idempotency key.
"""

from collections import defaultdict
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

import structlog
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.core.models import OutboxMessage, OutboxStatus

logger = structlog.get_logger(__name__)

Handler = Callable[[OutboxMessage], None]

MAX_ATTEMPTS = 10
LEASE = timedelta(minutes=5)
ERROR_MAX_CHARS = 2000

_handlers: dict[str, list[Handler]] = defaultdict(list)


def register(topic: str) -> Callable[[Handler], Handler]:
    """Subscribe a handler to a topic. Called from AppConfig.ready() via handlers modules."""

    def decorator(func: Handler) -> Handler:
        if func not in _handlers[topic]:
            _handlers[topic].append(func)
        return func

    return decorator


def handlers_for(topic: str) -> list[Handler]:
    return list(_handlers.get(topic, []))


def publish(
    *,
    topic: str,
    payload: dict[str, Any],
    dedupe_key: str | None = None,
    available_at: datetime | None = None,
) -> OutboxMessage:
    """Record an event in the current transaction. Duplicate `dedupe_key`s return the original."""
    fields: dict[str, Any] = {"topic": topic, "payload": payload, "dedupe_key": dedupe_key}
    if available_at is not None:
        fields["available_at"] = available_at
    try:
        with transaction.atomic():  # savepoint: a duplicate must not poison the outer transaction
            message = OutboxMessage.objects.create(**fields)
    except IntegrityError:
        if dedupe_key is None:
            raise
        return OutboxMessage.objects.get(dedupe_key=dedupe_key)

    public_id = str(message.public_id)
    transaction.on_commit(lambda: _kick(public_id), robust=True)
    return message


def _kick(public_id: str) -> None:
    from apps.core.tasks import relay_outbox_message  # noqa: PLC0415 — avoid an import cycle

    relay_outbox_message.delay(public_id)


def backoff(attempts: int) -> timedelta:
    """Exponential backoff: 30 s, 1 min, 2 min … capped at 6 h (≈24 h over 10 attempts)."""
    return min(timedelta(seconds=30 * 2 ** max(attempts - 1, 0)), timedelta(hours=6))


def claim(public_id: str | None = None) -> OutboxMessage | None:
    """Lease one due message. Returns None if nothing is due (or another worker holds it)."""
    now = timezone.now()
    with transaction.atomic():
        due = OutboxMessage.objects.select_for_update(skip_locked=True).filter(
            status=OutboxStatus.PENDING, available_at__lte=now
        )
        if public_id is not None:
            due = due.filter(public_id=public_id)
        message = due.order_by("available_at").first()
        if message is None:
            return None
        message.attempts += 1
        message.available_at = now + LEASE
        message.save(update_fields=["attempts", "available_at"])
    return message


def process(message: OutboxMessage) -> None:
    """Run every handler for the message, then settle it as dispatched, retried or dead."""
    handlers = handlers_for(message.topic)
    if not handlers:
        logger.warning("outbox.no_handler", topic=message.topic, message=str(message.public_id))
    try:
        for handler in handlers:
            handler(message)
    except Exception as exc:  # noqa: BLE001 — any handler failure is retried
        _settle_failure(message, exc)
        return
    OutboxMessage.objects.filter(pk=message.pk, status=OutboxStatus.PENDING).update(
        status=OutboxStatus.DISPATCHED, dispatched_at=timezone.now(), last_error=None
    )


def _settle_failure(message: OutboxMessage, exc: Exception) -> None:
    error = f"{type(exc).__name__}: {exc}"[:ERROR_MAX_CHARS]
    if message.attempts >= MAX_ATTEMPTS:
        status, available_at = OutboxStatus.DEAD, message.available_at
        logger.error("outbox.dead", topic=message.topic, message=str(message.public_id))
    else:
        status, available_at = OutboxStatus.PENDING, timezone.now() + backoff(message.attempts)
        logger.warning(
            "outbox.retry",
            topic=message.topic,
            message=str(message.public_id),
            attempts=message.attempts,
        )
    OutboxMessage.objects.filter(pk=message.pk).update(
        status=status, available_at=available_at, last_error=error
    )


def due_public_ids(limit: int = 500) -> list[str]:
    ids = (
        OutboxMessage.objects.filter(status=OutboxStatus.PENDING, available_at__lte=timezone.now())
        .order_by("available_at")
        .values_list("public_id", flat=True)[:limit]
    )
    return [str(i) for i in ids]
