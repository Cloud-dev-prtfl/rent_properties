import pytest
from django.db import DatabaseError, transaction
from django.test import RequestFactory

from apps.accounts.tests.factories import StaffUserFactory, UserFactory
from apps.core import audit
from apps.core.context import set_request_id
from apps.core.exceptions import DomainError
from apps.core.models import ActorType, AuditLog, OutboxMessage

pytestmark = pytest.mark.django_db


def test_audit_record_for_user_actor_and_target():
    actor, target = UserFactory(), UserFactory()
    set_request_id("req-12345678")
    try:
        entry = audit.record(action="auth.login", actor=actor, target=target, data={"via": "web"})
    finally:
        set_request_id(None)
    assert entry.actor_type == ActorType.USER
    assert entry.actor_public_id == actor.public_id
    assert entry.target_type == "accounts.user"
    assert entry.target_public_id == target.public_id
    assert entry.request_id == "req-12345678"


def test_audit_record_classifies_staff_and_system_actors():
    assert audit.record(action="ops.x", actor=StaffUserFactory()).actor_type == ActorType.STAFF
    system = audit.record(action="job.ran")
    assert system.actor_type == ActorType.SYSTEM
    assert system.actor_user is None


def test_audit_record_captures_request_metadata():
    request = RequestFactory().get("/", REMOTE_ADDR="203.0.113.7", HTTP_USER_AGENT="pytest-agent")
    entry = audit.record(action="page.viewed", request=request)
    assert entry.ip == "203.0.113.7"
    assert entry.user_agent == "pytest-agent"


def test_audit_record_rejects_pii_keys():
    with pytest.raises(audit.PIIInAuditDataError, match="email"):
        audit.record(action="profile.updated", data={"Email": "x@example.com"})


def test_audit_log_rows_cannot_be_updated_in_the_database():
    entry = audit.record(action="a.b")
    with pytest.raises(DatabaseError, match="append-only"), transaction.atomic():
        AuditLog.objects.filter(pk=entry.pk).update(action="tampered")


def test_immutable_model_refuses_save_and_delete_of_existing_rows():
    entry = audit.record(action="a.b")
    entry.action = "changed"
    with pytest.raises(TypeError, match="append-only"):
        entry.save()
    with pytest.raises(TypeError, match="cannot be deleted"):
        entry.delete()
    assert "a.b by SYSTEM" in str(AuditLog.objects.get(pk=entry.pk))


def test_outbox_message_str():
    message = OutboxMessage.objects.create(topic="x.y", payload={})
    assert str(message).startswith("x.y [PENDING]")


def test_domain_error_carries_stable_code():
    class InsufficientCreditsError(DomainError):
        code = "insufficient_credits"

    assert InsufficientCreditsError().code == "insufficient_credits"
    assert str(InsufficientCreditsError()) == "insufficient_credits"
    assert DomainError("boom", code="custom").code == "custom"
