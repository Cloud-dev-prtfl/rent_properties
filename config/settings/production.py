"""Settings for every AWS environment (dev, staging, prod). They differ only in env vars.

Missing required variables raise ImproperlyConfigured at startup (fail fast, US-004).
"""

from django.core.exceptions import ImproperlyConfigured

from .base import *

if DEBUG:
    raise ImproperlyConfigured("DJANGO_DEBUG must not be enabled with production settings.")

# Required in production even where base.py has a default.
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS")
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured("DJANGO_ALLOWED_HOSTS must list at least one host.")
if len(SECRET_KEY) < 50:  # noqa: PLR2004
    raise ImproperlyConfigured("DJANGO_SECRET_KEY must be at least 50 characters.")

# TLS terminates at the platform router or reverse proxy (Render/Heroku/Fly router, kamal-proxy,
# Traefik, Caddy), which sets X-Forwarded-Proto.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
# Health probes are answered by HealthCheckMiddleware before this redirect applies.
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 365
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_NAME = "__Host-sessionid"
CSRF_COOKIE_NAME = "__Host-csrftoken"
