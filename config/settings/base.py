"""Settings shared by every environment.

All environment-specific values come from environment variables (12-factor, US-004).
Every variable read here is listed in `.env.example`.
See docs/architecture/03-codebase-structure.md §6.
"""

from pathlib import Path

import environ
from csp.constants import NONCE, NONE, SELF
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _

from apps.core.logging import build_logging_config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()

# -------------------------------------------------------------------------------------------- core
SECRET_KEY = env.str("DJANGO_SECRET_KEY")
SECRET_KEY_FALLBACKS = env.list("DJANGO_SECRET_KEY_FALLBACKS", default=[])
DEBUG = env.bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])

APP_ENV = env.str("APP_ENV", default="local")  # local | dev | staging | prod — tagging only
# Release identifier for logs/Sentry. Falls back to what each hosting platform injects
# (ADR-0014): Render, Heroku (dyno metadata), Railway, Fly.io, Kamal, Coolify.
APP_RELEASE = next(
    (
        value
        for name in (
            "APP_RELEASE",
            "RENDER_GIT_COMMIT",
            "HEROKU_SLUG_COMMIT",
            "RAILWAY_GIT_COMMIT_SHA",
            "FLY_IMAGE_REF",
            "KAMAL_VERSION",
            "SOURCE_COMMIT",
        )
        if (value := env.str(name, default=""))
    ),
    "unversioned",
)

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Admin is never mounted at /admin/ (reconciliation register R-25).
ADMIN_URL_PREFIX = env.str("ADMIN_URL_PREFIX", default="ops/admin/")

# -------------------------------------------------------------------------------------------- apps
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "django.contrib.humanize",
    "django.contrib.postgres",
]
THIRD_PARTY_APPS = [
    "django_htmx",
    "template_partials",
    "csp",
    "waffle",
    "django_celery_beat",
]
LOCAL_APPS = [
    "apps.core",
    "apps.accounts",
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    # First: answers /healthz and /readyz before host validation and HTTPS redirects, because
    # platform health checkers (Render, Fly, kamal-proxy, Traefik) use internal hostnames.
    "apps.core.middleware.HealthCheckMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "apps.core.middleware.RequestContextMiddleware",
    "apps.core.middleware.ClientIPMiddleware",
    "apps.core.middleware.SecurityHeadersMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "waffle.middleware.WaffleMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "csp.context_processors.nonce",
            ],
        },
    },
]

# ------------------------------------------------------------------------------------- data stores
DATABASES = {
    "default": env.db("DATABASE_URL", engine="django.contrib.gis.db.backends.postgis"),
}
if env.str("DATABASE_REPLICA_URL", default=""):
    DATABASES["replica"] = env.db(
        "DATABASE_REPLICA_URL", engine="django.contrib.gis.db.backends.postgis"
    )
# "require" for managed databases reached over a network.
DATABASE_SSLMODE = env.str("DATABASE_SSLMODE", default="")
for _alias in DATABASES.values():
    _alias.update(ATOMIC_REQUESTS=False, CONN_MAX_AGE=60, CONN_HEALTH_CHECKS=True)
    if DATABASE_SSLMODE:
        _alias.setdefault("OPTIONS", {})["sslmode"] = DATABASE_SSLMODE

# PaaS add-ons usually expose one REDIS_URL; CACHE_URL / CELERY_BROKER_URL override it when a
# platform provides separate instances. A shared instance must run maxmemory-policy noeviction
# (the broker must never lose tasks); every cache key has a TTL (ADR-0014).
REDIS_URL = env.str("REDIS_URL", default="")
CACHE_URL = env.str("CACHE_URL", default=REDIS_URL)
if not CACHE_URL:
    raise ImproperlyConfigured("Set CACHE_URL or REDIS_URL.")
CACHES = {
    # General cache: an outage degrades to recomputation, never to errors.
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": CACHE_URL,
        "KEY_PREFIX": "c",
        "OPTIONS": {"IGNORE_EXCEPTIONS": True},
    },
    # Sessions: fail-soft, the cached_db engine falls back to PostgreSQL (register R-48).
    "sessions": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": CACHE_URL,
        "KEY_PREFIX": "s",
        "OPTIONS": {"IGNORE_EXCEPTIONS": True},
    },
    # Rate-limit counters: fail-CLOSED, so an outage refuses instead of silently allowing (R-48).
    "ratelimit": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": CACHE_URL,
        "KEY_PREFIX": "rl",
    },
}

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_CACHE_ALIAS = "sessions"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14
CSRF_COOKIE_HTTPONLY = True
CSRF_FAILURE_VIEW = "apps.core.views.csrf_failure"

# -------------------------------------------------------------------------------------------- auth
AUTH_USER_MODEL = "accounts.User"

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 10},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ----------------------------------------------------------------------------------- i18n (US-009)
LANGUAGE_CODE = "en"
LANGUAGES = [("en", _("English"))]
LOCALE_PATHS = [BASE_DIR / "locale"]
USE_I18N = True
USE_TZ = True
TIME_ZONE = "UTC"

# ---------------------------------------------------------------------------------- static & media
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# Only built and vendored assets are published; Tailwind sources (static/src/css) never are.
STATICFILES_DIRS = [
    ("dist", BASE_DIR / "static" / "dist"),
    ("vendor", BASE_DIR / "static" / "vendor"),
    ("js", BASE_DIR / "static" / "src" / "js"),
]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
STORAGES = {
    # S3 storages (apps.core.storage) replace the default in M2 (docs/design/05 §8).
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# ------------------------------------------------------------------------------------------- email
EMAIL_CONFIG = env.email_url("EMAIL_URL", default="consolemail://")
vars().update(EMAIL_CONFIG)
DEFAULT_FROM_EMAIL = env.str(
    "DEFAULT_FROM_EMAIL", default="Rent Property Listing <no-reply@localhost>"
)

# ----------------------------------------------------------------------- celery (config/celery.py)
CELERY_BROKER_URL = env.str("CELERY_BROKER_URL", default=REDIS_URL)
if not CELERY_BROKER_URL:
    raise ImproperlyConfigured("Set CELERY_BROKER_URL or REDIS_URL.")
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_IGNORE_RESULT = True
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_TIME_LIMIT = 300
CELERY_TASK_SOFT_TIME_LIMIT = 240
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# ----------------------------------------------------------------------- security headers (US-015)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
PERMISSIONS_POLICY = "camera=(), microphone=(), geolocation=(self), payment=(), usb=()"

# Strict CSP: no inline scripts or styles; the nonce exists for reviewed exceptions only (03 §8.5).
CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": [SELF],
        "script-src": [SELF, NONCE],
        "style-src": [SELF],
        "img-src": [SELF, "data:"],
        "font-src": [SELF],
        "connect-src": [SELF],
        "object-src": [NONE],
        "base-uri": [SELF],
        "form-action": [SELF],
        "frame-ancestors": [NONE],
    },
}

# ---------------------------------------------------------------------- client IP behind proxies
# Real client IP for rate limits and audit (apps.core.clientip). Configure ONE per platform:
#   CLIENT_IP_HEADER: a header set by a trusted edge, e.g. CF-Connecting-IP (Cloudflare),
#                     Fly-Client-IP (Fly.io). Never set this unless that edge is always in front.
#   TRUSTED_PROXY_COUNT: number of proxies appending to X-Forwarded-For (Heroku/Render router,
#                     kamal-proxy, Traefik, Caddy: usually 1). 0 = use REMOTE_ADDR.
CLIENT_IP_HEADER = env.str("CLIENT_IP_HEADER", default="")
TRUSTED_PROXY_COUNT = env.int("TRUSTED_PROXY_COUNT", default=0)

# ----------------------------------------------------------------------------------- feature flags
WAFFLE_CREATE_MISSING_FLAGS = False
WAFFLE_CREATE_MISSING_SWITCHES = False

# ----------------------------------------------------------------------------------------- logging
LOG_LEVEL = env.str("LOG_LEVEL", default="INFO")
LOG_JSON = env.bool("LOG_JSON", default=True)
LOGGING = build_logging_config(level=LOG_LEVEL, json=LOG_JSON)

# ----------------------------------------------------------------------------------- observability
SENTRY_DSN = env.str("SENTRY_DSN", default="")
SENTRY_TRACES_SAMPLE_RATE = env.float("SENTRY_TRACES_SAMPLE_RATE", default=0.0)
OTEL_ENABLED = env.bool("OTEL_ENABLED", default=False)

# -------------------------------------------------------------------- business constants (03 §6.3)
CREDITS_REVEAL_COST = 2
CREDITS_SIGNUP_PROMO = 10
LISTINGS_MIN_IMAGES = 3
LISTINGS_MAX_IMAGES = 20
LISTINGS_MAX_IMAGE_BYTES = 5_242_880
LISTINGS_MAX_OPEN_DRAFTS = 10
SEARCH_CACHE_TTL_SECONDS = 120
