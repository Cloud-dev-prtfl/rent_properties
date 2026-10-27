"""Developer settings (the `manage.py` default). Used inside the docker compose stack."""

from .base import *

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "web"]
CSRF_TRUSTED_ORIGINS = ["http://localhost:8000", "http://localhost:8080"]

# Readable console logs locally; JSON everywhere else.
LOGGING = build_logging_config(level=LOG_LEVEL, json=env.bool("LOG_JSON", default=False))

# Plain static storage so templates work without running collectstatic.
STORAGES["staticfiles"] = {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}
WHITENOISE_AUTOREFRESH = True
