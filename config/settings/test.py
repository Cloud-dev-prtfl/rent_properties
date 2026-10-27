"""pytest settings. Tests run against real PostgreSQL + PostGIS, never SQLite."""

import os

os.environ.setdefault("DJANGO_SECRET_KEY", "test-only-secret-key-not-for-production")
os.environ.setdefault("DATABASE_URL", "postgis://rpl:rpl@localhost:5432/rpl")
os.environ.setdefault("CACHE_URL", "redis://localhost:6379/1")
os.environ.setdefault("CELERY_BROKER_URL", "memory://")

from .base import *

DEBUG = False
ALLOWED_HOSTS = ["testserver", "localhost"]

# Tests only: a fast hasher. Production hashing is asserted separately.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Isolated in-process caches; tests that need Redis behaviour use fakes explicitly.
CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": "default"},
    "sessions": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": "s"},
    "ratelimit": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": "rl"},
}

STORAGES["staticfiles"] = {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}

LOGGING = build_logging_config(level="WARNING", json=False)

# Find static files at request time; avoids scanning a STATIC_ROOT that tests never build.
WHITENOISE_AUTOREFRESH = True
