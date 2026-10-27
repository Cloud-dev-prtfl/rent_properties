"""Production settings must fail fast on bad configuration (US-004).

Each case runs in a subprocess so settings import from a clean environment.
"""

import os
import subprocess
import sys

import pytest

VALID_ENV = {
    "DJANGO_SETTINGS_MODULE": "config.settings.production",
    "DJANGO_SECRET_KEY": "x" * 60,
    "DJANGO_ALLOWED_HOSTS": "example.com",
    "DJANGO_CSRF_TRUSTED_ORIGINS": "https://example.com",
    "DATABASE_URL": "postgis://u:p@db:5432/rpl",
    "CACHE_URL": "redis://valkey:6379/0",
    "CELERY_BROKER_URL": "redis://valkey:6379/1",
}
PROBE = (
    "import django; from django.conf import settings; django.setup(); "
    "print(settings.DEBUG, settings.PASSWORD_HASHERS[0].rsplit('.', 1)[1], "
    "settings.SECURE_SSL_REDIRECT)"
)


def run_with(
    env_changes: dict[str, str | None], probe: str = PROBE
) -> subprocess.CompletedProcess[str]:
    isolated = ("DJANGO_", "DATABASE_", "CACHE_", "CELERY_", "REDIS_", "APP_")
    env = {k: v for k, v in os.environ.items() if not k.startswith(isolated)}
    env.update(VALID_ENV)
    for key, value in env_changes.items():
        if value is None:
            env.pop(key, None)
        else:
            env[key] = value
    return subprocess.run(  # noqa: S603 — fixed interpreter and arguments
        [sys.executable, "-c", probe], env=env, capture_output=True, text=True, check=False
    )


def test_valid_production_configuration_loads_with_safe_defaults():
    result = run_with({})
    assert result.returncode == 0, result.stderr
    assert result.stdout.split() == ["False", "Argon2PasswordHasher", "True"]


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"DJANGO_DEBUG": "true"}, "DJANGO_DEBUG must not be enabled"),
        ({"DJANGO_SECRET_KEY": None}, "DJANGO_SECRET_KEY"),
        ({"DJANGO_SECRET_KEY": "too-short"}, "at least 50 characters"),
        ({"DJANGO_ALLOWED_HOSTS": None}, "DJANGO_ALLOWED_HOSTS"),
        ({"DATABASE_URL": None}, "DATABASE_URL"),
    ],
)
def test_bad_production_configuration_fails_fast(changes, message):
    result = run_with(changes)
    assert result.returncode != 0
    assert message in result.stderr


def test_paas_style_single_redis_url_configures_cache_and_broker():
    probe = (
        "import django; from django.conf import settings; django.setup(); "
        "print(settings.CACHES['default']['LOCATION'], settings.CELERY_BROKER_URL)"
    )
    result = run_with(
        {"CACHE_URL": None, "CELERY_BROKER_URL": None, "REDIS_URL": "rediss://h:6380/0"}, probe
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.split() == ["rediss://h:6380/0", "rediss://h:6380/0"]


def test_missing_redis_configuration_fails_fast():
    result = run_with({"CACHE_URL": None, "CELERY_BROKER_URL": None})
    assert result.returncode != 0
    assert "Set CACHE_URL or REDIS_URL" in result.stderr


@pytest.mark.parametrize(
    ("variable", "value"),
    [("RENDER_GIT_COMMIT", "abc123"), ("HEROKU_SLUG_COMMIT", "def456"), ("APP_RELEASE", "v1")],
)
def test_release_identifier_falls_back_to_platform_variables(variable, value):
    probe = "from django.conf import settings; print(settings.APP_RELEASE)"
    result = run_with({variable: value}, probe)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == value


def test_database_sslmode_is_applied_when_set():
    probe = "from django.conf import settings; print(settings.DATABASES['default']['OPTIONS'])"
    result = run_with({"DATABASE_SSLMODE": "require"}, probe)
    assert result.returncode == 0, result.stderr
    assert "'sslmode': 'require'" in result.stdout
