"""Audit trail writer (docs/design/01-domain-model.md §2.2). Never put PII values in `data`."""

from typing import Any

from django.db import models
from django.http import HttpRequest

from apps.core.context import get_request_id
from apps.core.models import ActorType, AuditLog

PII_KEYS = frozenset(
    {"email", "phone", "phone_e164", "password", "full_name", "name", "address", "token", "otp"}
)


class PIIInAuditDataError(ValueError):
    pass


def record(
    *,
    action: str,
    actor: Any = None,
    actor_type: str | None = None,
    target: models.Model | None = None,
    data: dict[str, Any] | None = None,
    request: HttpRequest | None = None,
) -> AuditLog:
    data = data or {}
    leaked = PII_KEYS.intersection(k.lower() for k in data)
    if leaked:
        raise PIIInAuditDataError(f"Audit data must not contain PII keys: {sorted(leaked)}")

    if actor is not None and getattr(actor, "is_authenticated", False):
        resolved_type = actor_type or (ActorType.STAFF if actor.is_staff else ActorType.USER)
        actor_user, actor_public_id = actor, actor.public_id
    else:
        resolved_type = actor_type or ActorType.SYSTEM
        actor_user, actor_public_id = None, None

    entry = AuditLog(
        action=action,
        actor_type=resolved_type,
        actor_user=actor_user,
        actor_public_id=actor_public_id,
        data=data,
        request_id=get_request_id(),
    )
    if target is not None:
        entry.target_type = target._meta.label_lower
        entry.target_public_id = getattr(target, "public_id", None)
    if request is not None:
        entry.ip = getattr(request, "client_ip", None) or request.META.get("REMOTE_ADDR")
        entry.user_agent = request.headers.get("User-Agent", "")[:255]
    entry.save()
    return entry
