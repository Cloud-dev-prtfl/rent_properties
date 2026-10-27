import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

application = get_wsgi_application()

from apps.core.telemetry import configure_telemetry  # noqa: E402 — needs configured settings

configure_telemetry(service_role="web")
