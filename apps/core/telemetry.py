"""Sentry and OpenTelemetry bootstrap. Both are optional and switched on by settings.

Called once per process: from config/wsgi.py (web) and the Celery worker_process_init signal.
"""

from typing import Any

import structlog
from django.conf import settings

from apps.core.logging import SENSITIVE_KEYS

logger = structlog.get_logger(__name__)
_configured: set[str] = set()


def scrub_event(event: Any, _hint: Any) -> Any:
    """Sentry before_send: drop cookies and redact sensitive request fields."""
    request = event.get("request") or {}
    request.pop("cookies", None)
    for section in ("data", "headers"):
        values = request.get(section)
        if isinstance(values, dict):
            for key in values:
                if key.lower() in SENSITIVE_KEYS:
                    values[key] = "[REDACTED]"
    return event


def configure_telemetry(*, service_role: str) -> None:
    if service_role in _configured:
        return
    _configured.add(service_role)

    if settings.SENTRY_DSN:
        import sentry_sdk  # noqa: PLC0415

        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.APP_ENV,
            release=settings.APP_RELEASE,
            send_default_pii=False,
            traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
            before_send=scrub_event,
        )
        sentry_sdk.set_tag("service_role", service_role)

    if settings.OTEL_ENABLED:
        _configure_otel(service_role)

    logger.info("telemetry.configured", service_role=service_role, sentry=bool(settings.SENTRY_DSN))


def _configure_otel(service_role: str) -> None:  # pragma: no cover — exercised on deployed envs
    from opentelemetry import trace  # noqa: PLC0415
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import (  # noqa: PLC0415
        OTLPSpanExporter,
    )
    from opentelemetry.instrumentation.celery import CeleryInstrumentor  # noqa: PLC0415
    from opentelemetry.instrumentation.django import DjangoInstrumentor  # noqa: PLC0415
    from opentelemetry.instrumentation.psycopg import PsycopgInstrumentor  # noqa: PLC0415
    from opentelemetry.instrumentation.redis import RedisInstrumentor  # noqa: PLC0415
    from opentelemetry.sdk.resources import Resource  # noqa: PLC0415
    from opentelemetry.sdk.trace import TracerProvider  # noqa: PLC0415
    from opentelemetry.sdk.trace.export import BatchSpanProcessor  # noqa: PLC0415

    resource = Resource.create(
        {
            "service.name": "rpl",
            "service.namespace": settings.APP_ENV,
            "service.version": settings.APP_RELEASE,
            "rpl.role": service_role,
        }
    )
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))  # OTEL_EXPORTER_* env vars
    trace.set_tracer_provider(provider)
    DjangoInstrumentor().instrument()
    PsycopgInstrumentor().instrument(enable_commenter=False)
    CeleryInstrumentor().instrument()
    RedisInstrumentor().instrument()
