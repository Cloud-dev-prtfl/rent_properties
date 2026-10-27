from datetime import timedelta

import pytest
from django.db import IntegrityError
from django.utils import timezone

from apps.core import outbox, tasks
from apps.core.models import OutboxMessage, OutboxStatus

pytestmark = pytest.mark.django_db

TOPIC = "test.happened"


@pytest.fixture(autouse=True)
def _isolated_registry(monkeypatch):
    monkeypatch.setattr(outbox, "_handlers", outbox.defaultdict(list))


@pytest.fixture
def kicked(monkeypatch):
    calls: list[str] = []
    monkeypatch.setattr(tasks.relay_outbox_message, "delay", calls.append)
    return calls


def test_publish_writes_pending_row_and_kicks_relay_after_commit(
    django_capture_on_commit_callbacks, kicked
):
    with django_capture_on_commit_callbacks(execute=True):
        message = outbox.publish(topic=TOPIC, payload={"id": "abc"})
    assert message.status == OutboxStatus.PENDING
    assert kicked == [str(message.public_id)]


def test_publish_does_not_kick_when_transaction_rolls_back(
    django_capture_on_commit_callbacks, kicked
):
    with django_capture_on_commit_callbacks() as callbacks:
        outbox.publish(topic=TOPIC, payload={})
    # Callbacks are captured but never executed, as on rollback.
    assert len(callbacks) == 1
    assert kicked == []


def test_duplicate_dedupe_key_returns_original_without_new_row(kicked):
    first = outbox.publish(topic=TOPIC, payload={"n": 1}, dedupe_key="k-1")
    second = outbox.publish(topic=TOPIC, payload={"n": 2}, dedupe_key="k-1")
    assert second.pk == first.pk
    assert OutboxMessage.objects.count() == 1


def test_publish_reraises_integrity_errors_without_dedupe_key(kicked):
    with pytest.raises(IntegrityError):
        outbox.publish(topic=TOPIC, payload=["not", "an", "object"])  # type: ignore[arg-type]


def test_publish_honours_delayed_availability(kicked):
    later = timezone.now() + timedelta(hours=1)
    message = outbox.publish(topic=TOPIC, payload={}, available_at=later)
    assert outbox.claim(str(message.public_id)) is None


def test_claim_leases_message_so_a_second_claim_gets_nothing(kicked):
    message = outbox.publish(topic=TOPIC, payload={})
    claimed = outbox.claim(str(message.public_id))
    assert claimed is not None
    assert claimed.attempts == 1
    assert claimed.available_at > timezone.now()
    assert outbox.claim(str(message.public_id)) is None


def test_process_dispatches_when_handlers_succeed(kicked):
    seen: list[str] = []
    outbox.register(TOPIC)(lambda m: seen.append(m.payload["id"]))
    message = outbox.publish(topic=TOPIC, payload={"id": "p-1"})
    outbox.process(outbox.claim(str(message.public_id)))
    message.refresh_from_db()
    assert seen == ["p-1"]
    assert message.status == OutboxStatus.DISPATCHED
    assert message.dispatched_at is not None


def test_register_is_idempotent():
    def handler(_m):
        return None

    outbox.register(TOPIC)(handler)
    outbox.register(TOPIC)(handler)
    assert outbox.handlers_for(TOPIC) == [handler]


def test_failed_handler_schedules_retry_with_backoff(kicked):
    def boom(_m):
        raise RuntimeError("provider down")

    outbox.register(TOPIC)(boom)
    message = outbox.publish(topic=TOPIC, payload={})
    outbox.process(outbox.claim(str(message.public_id)))
    message.refresh_from_db()
    assert message.status == OutboxStatus.PENDING
    assert message.last_error == "RuntimeError: provider down"
    assert message.available_at > timezone.now() + timedelta(seconds=20)


def test_message_goes_dead_after_max_attempts(kicked):
    def boom(_m):
        raise RuntimeError("still down")

    outbox.register(TOPIC)(boom)
    message = outbox.publish(topic=TOPIC, payload={})
    OutboxMessage.objects.filter(pk=message.pk).update(attempts=outbox.MAX_ATTEMPTS - 1)
    outbox.process(outbox.claim(str(message.public_id)))
    message.refresh_from_db()
    assert message.status == OutboxStatus.DEAD


def test_message_without_handler_is_marked_dispatched(kicked):
    message = outbox.publish(topic="nobody.listens", payload={})
    outbox.process(outbox.claim(str(message.public_id)))
    message.refresh_from_db()
    assert message.status == OutboxStatus.DISPATCHED


@pytest.mark.parametrize(
    ("attempts", "expected"),
    [(1, timedelta(seconds=30)), (2, timedelta(minutes=1)), (20, timedelta(hours=6))],
)
def test_backoff_is_exponential_and_capped(attempts, expected):
    assert outbox.backoff(attempts) == expected


def test_relay_task_claims_and_processes(kicked):
    message = outbox.publish(topic=TOPIC, payload={})
    tasks.relay_outbox_message(str(message.public_id))
    message.refresh_from_db()
    assert message.status == OutboxStatus.DISPATCHED


def test_relay_task_is_a_noop_for_unknown_message():
    tasks.relay_outbox_message("00000000-0000-0000-0000-000000000000")


def test_sweep_enqueues_only_due_messages(kicked):
    due = outbox.publish(topic=TOPIC, payload={})
    outbox.publish(topic=TOPIC, payload={}, available_at=timezone.now() + timedelta(hours=1))
    kicked.clear()
    assert tasks.sweep_outbox() == 1
    assert kicked == [str(due.public_id)]


def test_ping_task():
    assert tasks.ping() == "pong"
