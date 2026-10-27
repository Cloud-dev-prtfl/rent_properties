"""Liveness and readiness endpoints for the ALB and ECS (US-006)."""

import uuid
from collections.abc import Callable

import structlog
from django.conf import settings
from django.core.cache import caches
from django.db import connections
from django.http import HttpRequest, JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET
from kombu import Connection

logger = structlog.get_logger(__name__)
BROKER_TIMEOUT_SECONDS = 2


@never_cache
@require_GET
def healthz(_request: HttpRequest) -> JsonResponse:
    """Liveness: the process can serve HTTP. Never touches dependencies."""
    return JsonResponse({"status": "ok"})


def check_database() -> None:
    with connections["default"].cursor() as cursor:
        cursor.execute("SELECT 1")


def check_cache() -> None:
    # The default alias swallows errors, so verify with a write-then-read round trip.
    cache = caches["default"]
    key, value = f"readyz:{uuid.uuid4().hex}", "1"
    cache.set(key, value, timeout=10)
    if cache.get(key) != value:
        raise ConnectionError("cache round trip failed")
    cache.delete(key)


def check_broker() -> None:
    with Connection(settings.CELERY_BROKER_URL, connect_timeout=BROKER_TIMEOUT_SECONDS) as conn:
        conn.ensure_connection(max_retries=1, timeout=BROKER_TIMEOUT_SECONDS)


CHECKS: dict[str, Callable[[], None]] = {
    "database": check_database,
    "cache": check_cache,
    "broker": check_broker,
}


@never_cache
@require_GET
def readyz(_request: HttpRequest) -> JsonResponse:
    """Readiness: dependencies are reachable. 503 takes the task out of the target group."""
    results: dict[str, str] = {}
    for name, check in CHECKS.items():
        try:
            check()
        except Exception as exc:  # noqa: BLE001 — any failure means not ready
            logger.warning("readyz.check_failed", check=name, error=type(exc).__name__)
            results[name] = "error"
        else:
            results[name] = "ok"
    ready = all(v == "ok" for v in results.values())
    return JsonResponse(
        {"status": "ok" if ready else "error", "checks": results}, status=200 if ready else 503
    )
