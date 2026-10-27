# syntax=docker/dockerfile:1.7
# One image for every process (web, worker, beat, migrate). Targets:
#   dev     — all dependency groups, used by docker compose and CI tests (code is bind-mounted)
#   runtime — production image: no dev tools, collected static files, non-root
# Runs unchanged on PaaS (Render, Railway, Heroku, Fly.io) and self-hosted (compose, Kamal,
# Coolify). See docs/architecture/05-hosting-and-deployment.md and ADR-0014.

ARG PYTHON_IMAGE=python:3.13-slim-trixie

FROM ghcr.io/astral-sh/uv:0.8.15 AS uv

# ---------------------------------------------------------------- base: OS libraries for GeoDjango
FROM ${PYTHON_IMAGE} AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy
RUN apt-get update \
    && apt-get install -y --no-install-recommends gdal-bin gettext \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app --home-dir /app --shell /usr/sbin/nologin app
WORKDIR /app

# ---------------------------------------------------------------- assets: Tailwind build
FROM base AS assets
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY scripts/fetch-tailwind.sh scripts/
RUN scripts/fetch-tailwind.sh /usr/local/bin/tailwindcss
COPY static/src static/src
COPY templates templates
COPY apps apps
RUN tailwindcss -i static/src/css/app.css -o static/dist/app.css --minify

# ---------------------------------------------------------------- deps: production dependencies
FROM base AS deps
COPY --from=uv /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# ---------------------------------------------------------------- dev: + dev tools, Tailwind CLI
FROM deps AS dev
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates make git \
    && rm -rf /var/lib/apt/lists/*
COPY scripts/fetch-tailwind.sh scripts/
RUN scripts/fetch-tailwind.sh /usr/local/bin/tailwindcss
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project
ENV DJANGO_SETTINGS_MODULE=config.settings.local
EXPOSE 8000
CMD ["gunicorn", "config.wsgi", "-c", "docker/gunicorn.conf.py", "--reload"]

# ---------------------------------------------------------------- runtime: production image
FROM base AS runtime
ARG APP_RELEASE=unversioned
ENV DJANGO_SETTINGS_MODULE=config.settings.production \
    APP_RELEASE=${APP_RELEASE}
COPY --from=deps /opt/venv /opt/venv
COPY --chown=app:app . .
COPY --from=assets --chown=app:app /app/static/dist static/dist
# collectstatic needs settings to import; these placeholder values exist only for this step.
RUN export DJANGO_SECRET_KEY=build-only-placeholder-secret-key-that-is-long-enough-1234567890 \
        DJANGO_ALLOWED_HOSTS=build DJANGO_CSRF_TRUSTED_ORIGINS=https://build \
        DATABASE_URL=postgis://build@localhost/build CACHE_URL=redis://localhost:6379/0 \
        CELERY_BROKER_URL=redis://localhost:6379/1 \
    && python manage.py collectstatic --noinput \
    && python manage.py compilemessages \
    && chown -R app:app staticfiles
USER app
EXPOSE 8000
# Process type is chosen by the platform: bin/web (default), bin/worker, bin/beat, bin/release.
CMD ["bin/web"]
