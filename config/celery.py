"""Celery application. Queue routing is declared once, here (03 §10, register R-46)."""

import os

from celery import Celery
from celery.signals import worker_process_init
from kombu import Queue

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("rpl")
app.config_from_object("django.conf:settings", namespace="CELERY")

# Keep Django's LOGGING (structlog JSON) instead of Celery's own root-logger setup.
app.conf.worker_hijack_root_logger = False
app.conf.task_default_queue = "default"
app.conf.task_queues = (Queue("default"), Queue("maintenance"), Queue("media"))
app.conf.task_routes = {
    "core.sweep_outbox": {"queue": "maintenance"},
    "core.ping": {"queue": "default"},
    "core.relay_outbox_message": {"queue": "default"},
}
app.conf.beat_schedule = {
    # The sweeper re-dispatches outbox rows whose on_commit kick was lost (ADR-0006).
    "core.sweep_outbox": {"task": "core.sweep_outbox", "schedule": 30.0},
}

app.autodiscover_tasks()


@worker_process_init.connect
def _init_worker_telemetry(**_kwargs: object) -> None:
    from apps.core.telemetry import configure_telemetry  # noqa: PLC0415 — after Django setup

    configure_telemetry(service_role="worker")
