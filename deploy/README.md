# Deployment

One container image (`docker/Dockerfile`, last stage `runtime`) and four process scripts (`bin/web`, `bin/worker`, `bin/beat`, `bin/release`) run on every target. Design and rationale: [docs/architecture/05-hosting-and-deployment.md](../docs/architecture/05-hosting-and-deployment.md) and [ADR-0014](../docs/adr/0014-portable-hosting-paas-and-self-hosted.md).

| Target | Files | Start |
|---|---|---|
| Render | `render.yaml` | Dashboard → New Blueprint → this repo; fill the `sync: false` variables |
| Heroku | `heroku.yml`, `Procfile` | `heroku stack:set container`, add Postgres + Key-Value Store, `git push heroku main`, `heroku ps:scale web=2 worker=1 beat=1` |
| Fly.io | `fly.toml` | `fly launch --no-deploy` (keep the file), `fly secrets set …`, `fly deploy`, `fly scale count beat=1` |
| Railway | Dockerfile | Three services from this repo: `bin/web` (pre-deploy `bin/release`, health `/healthz`), `bin/worker`, `bin/beat` (1 replica); add Postgres (PostGIS) + Redis |
| Docker Compose (VPS) | `deploy/compose/` | `cp deploy/compose/.env.prod.example deploy/compose/.env.prod`, edit, then `docker compose --env-file deploy/compose/.env.prod -f deploy/compose/compose.prod.yaml --profile proxy up -d --build` |
| Coolify | `deploy/compose/compose.prod.yaml` | Docker Compose resource **without** the `proxy` profile; set the domain on `web:8000` |
| Kamal 2 | `deploy/kamal/` | `cp deploy/kamal/secrets.example .kamal/secrets`, edit hosts/registry/domain, `kamal setup -c deploy/kamal/deploy.yml` |

Every target needs:
- PostgreSQL 17 with **PostGIS** and **pg_trgm**;
- Redis/Valkey with `maxmemory-policy noeviction` when shared;
- **exactly one** `beat` process;
- `TRUSTED_PROXY_COUNT` (or `CLIENT_IP_HEADER`) set for the proxy in front.

The full variable list is in the hosting guide §3.
