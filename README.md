# Rent Property Listing

A credit-based rental marketplace. Listers (owners and agents) post properties; renters spend credits to reveal a lister's contact details. It is built as a Django 5.2 LTS modular monolith with server-rendered templates, HTMX, Alpine.js and Tailwind, on PostgreSQL 17 + PostGIS, Valkey and Celery. One container image deploys to a PaaS (Render, Railway, Heroku, Fly.io) or to self-hosted servers (Docker Compose, Kamal, Coolify); see [`deploy/`](deploy/README.md).

- **Design and plan:** [`docs/README.md`](docs/README.md) (requirements, architecture, ADRs, milestones)
- **Status:** M0 (foundations) complete; deployment deferred, with the hosting target to be chosen later ([ADR-0014](docs/adr/0014-portable-hosting-paas-and-self-hosted.md))

## Quick start

Prerequisites: Docker Desktop (or Docker Engine with Compose v2.24+), `make`, `curl`. The Python tooling runs inside the dev container, so no local Python, GDAL or PostgreSQL is needed.

```bash
make up          # builds CSS + the dev image, starts the stack, applies migrations
open http://localhost:8080          # app via Nginx  (Gunicorn directly: http://localhost:8000)
open http://localhost:8025          # Mailpit (captured email)
make superuser   # ops admin at http://localhost:8080/ops/admin/
```

Health: `curl localhost:8000/healthz` (liveness) and `curl localhost:8000/readyz` (database, cache, broker).

## Everyday commands

| Command | What it does |
|---|---|
| `make check` | Full quality gate: ruff, format, mypy, import contracts, djLint, migrations check, bandit, pytest with a 90 % coverage gate, vendored-JS hashes |
| `make test` / `make test-fast` | Tests with coverage / fail-fast without coverage |
| `make fmt` | Format Python and templates |
| `make css-watch` | Rebuild Tailwind on change |
| `make logs` / `make down` | Follow logs / stop the stack |
| `make e2e` | Playwright + axe smoke against the running stack (one-time setup: `uv sync --group e2e && uv run playwright install chromium`) |
| `make image` | Build the production image |

Install the git hooks once: `uv tool install pre-commit && pre-commit install`.

## Services in the local stack

| Service | Purpose | Port |
|---|---|---|
| `web` | Gunicorn (auto-reload) | 8000 |
| `nginx` | Local reverse proxy (not used in AWS) | 8080 |
| `worker` / `beat` | Celery worker (queues `default`, `maintenance`, `media`) and scheduler | — |
| `db` | PostgreSQL 17 + PostGIS 3.5 + pg_trgm | 5432 |
| `valkey` | Cache, sessions, Celery broker | 6379 |
| `mailpit` | Email capture | 8025 |
| `s3` | SeaweedFS S3 emulator (used from M2) | 8333 |

## Repository layout

`config/` holds the settings (base, local, test, production), URLs and Celery. The apps live in `apps/<app>/`, with services for writes and selectors for reads. Templates are in `templates/` and static assets in `static/`. Container files are in `docker/`, process scripts in `bin/`, deployment manifests in `deploy/` and the repo root, database bootstrap SQL in `infra/sql/`, and tests in `tests/`. See [codebase structure](docs/architecture/03-codebase-structure.md).

## Configuration

All configuration comes from environment variables, and every one is listed in [`.env.example`](.env.example). Copy it to `.env` to override locally. Production settings refuse to start if a required variable is missing or `DJANGO_DEBUG` is on.

## Deployment

The same image runs everywhere; only the manifest differs. See [`deploy/README.md`](deploy/README.md) for commands and [Hosting and deployment](docs/architecture/05-hosting-and-deployment.md) for the design.

| Target | Manifest |
|---|---|
| Render | `render.yaml` |
| Heroku | `heroku.yml` + `Procfile` |
| Fly.io | `fly.toml` |
| Railway | Dockerfile + per-service start commands (`bin/web`, `bin/worker`, `bin/beat`) |
| Docker Compose / Coolify | `deploy/compose/compose.prod.yaml` |
| Kamal 2 | `deploy/kamal/deploy.yml` |

Deployment is deferred by decision: no environment is provisioned yet, and the CI deploy job is written once a target is chosen.
