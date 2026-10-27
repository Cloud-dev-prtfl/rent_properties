"""Celery tasks for platform mechanisms. Tasks take primitives and delegate to modules."""

import structlog
from celery import shared_task

from apps.core import outbox

logger = structlog.get_logger(__name__)


@shared_task(name="core.ping")
def ping() -> str:
    """Smoke-test task: proves broker, worker and logging work end to end (M0 demo step 4)."""
    logger.info("core.ping")
    return "pong"


@shared_task(name="core.relay_outbox_message", acks_late=True)
def relay_outbox_message(public_id: str) -> None:
    message = outbox.claim(public_id)
    if message is not None:
        outbox.process(message)


@shared_task(name="core.sweep_outbox")
def sweep_outbox() -> int:
    """Re-dispatch due messages whose on_commit kick was lost (broker outage, crash)."""
    ids = outbox.due_public_ids()
    for public_id in ids:
        relay_outbox_message.delay(public_id)
    return len(ids)
