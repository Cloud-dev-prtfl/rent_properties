"""Shared base classes and platform tables (docs/design/01-domain-model.md §0.1, §2)."""

import uuid
from typing import Any, ClassVar

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    # default=timezone.now (not auto_now_add) so services may set it explicitly.
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class PublicIdModel(models.Model):
    """The UUID is the only identifier allowed in URLs, HTML, emails, logs and payloads (R10)."""

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    class Meta:
        abstract = True


class ImmutableModel(models.Model):
    """Defence in depth for append-only tables; database triggers are authoritative."""

    class Meta:
        abstract = True

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.pk is not None and not self._state.adding:
            raise TypeError(f"{type(self).__name__} rows are append-only.")
        super().save(*args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        raise TypeError(f"{type(self).__name__} rows cannot be deleted.")


class OutboxStatus(models.TextChoices):
    PENDING = "PENDING", _("Pending")
    DISPATCHED = "DISPATCHED", _("Dispatched")
    DEAD = "DEAD", _("Dead")


class OutboxMessage(PublicIdModel):
    """Written inside the business transaction and relayed after commit (ADR-0006).

    Payloads carry public IDs only, never PII or contact details.
    """

    topic = models.CharField(max_length=100)
    payload = models.JSONField(default=dict)
    dedupe_key = models.CharField(max_length=200, null=True, blank=True)
    status = models.CharField(
        max_length=12, choices=OutboxStatus.choices, default=OutboxStatus.PENDING
    )
    attempts = models.PositiveSmallIntegerField(default=0)
    available_at = models.DateTimeField(default=timezone.now)
    last_error = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    dispatched_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["dedupe_key"], name="uq_outbox_dedupe_key"),
            models.CheckConstraint(
                condition=Q(status__in=OutboxStatus.values), name="ck_outbox_status_valid"
            ),
        ]
        indexes: ClassVar = [
            models.Index(
                fields=["available_at"],
                name="ix_outbox_pending",
                condition=Q(status=OutboxStatus.PENDING),
            ),
            models.Index(
                fields=["created_at"], name="ix_outbox_dead", condition=Q(status=OutboxStatus.DEAD)
            ),
        ]

    def __str__(self) -> str:
        return f"{self.topic} [{self.status}] {self.public_id}"


class ActorType(models.TextChoices):
    USER = "USER", _("User")
    STAFF = "STAFF", _("Staff")
    SYSTEM = "SYSTEM", _("System")


class AuditLog(PublicIdModel, ImmutableModel):
    """Append-only security/audit trail. UPDATE is blocked by a database trigger."""

    occurred_at = models.DateTimeField(default=timezone.now, editable=False)
    actor_type = models.CharField(max_length=10, choices=ActorType.choices)
    # No FK constraint: purging a user must never conflict with audit history.
    actor_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        db_constraint=False,
        related_name="+",
    )
    actor_public_id = models.UUIDField(null=True, blank=True)
    action = models.CharField(max_length=100)
    target_type = models.CharField(max_length=50, null=True, blank=True)
    target_public_id = models.UUIDField(null=True, blank=True)
    request_id = models.CharField(max_length=64, null=True, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)
    data = models.JSONField(default=dict)

    class Meta:
        constraints: ClassVar = [
            models.CheckConstraint(
                condition=Q(actor_type__in=ActorType.values), name="ck_auditlog_actor_type_valid"
            ),
        ]
        indexes: ClassVar = [
            models.Index(fields=["action", "-occurred_at"], name="ix_auditlog_action_time"),
            models.Index(fields=["target_type", "target_public_id"], name="ix_auditlog_target"),
        ]

    def __str__(self) -> str:
        return f"{self.action} by {self.actor_type} at {self.occurred_at:%Y-%m-%d %H:%M:%S}"
