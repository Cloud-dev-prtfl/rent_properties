# Developer entry points (docs/architecture/03-codebase-structure.md §15).
# Python tooling runs inside the dev container (GDAL/GEOS live there); CSS builds on the host.

COMPOSE ?= docker compose
RUN     := $(COMPOSE) run --rm --no-deps -e DJANGO_SETTINGS_MODULE=config.settings.test web
MANAGE  := $(COMPOSE) exec web python manage.py
TAILWIND := .tools/tailwindcss

.DEFAULT_GOAL := help
.PHONY: help up down logs build migrate seed shell superuser check lint fmt typecheck test test-fast \
        e2e css css-watch tools vendor-verify messages image

help: ## List targets
	@grep -E '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "} {printf "  %-14s %s\n", $$1, $$2}'

# ------------------------------------------------------------------ stack
up: css ## Start the local stack (http://localhost:8080)
	$(COMPOSE) up -d --build
down: ## Stop the local stack
	$(COMPOSE) down
logs: ## Follow logs of all services
	$(COMPOSE) logs -f --tail=100
build: ## Rebuild the dev image
	$(COMPOSE) build web
migrate: ## Apply migrations
	$(MANAGE) migrate
seed: ## Load demo data (grows with each milestone)
	$(MANAGE) check
shell: ## Django shell in the web container
	$(MANAGE) shell
superuser: ## Create an ops superuser
	$(MANAGE) createsuperuser

# ------------------------------------------------------------------ quality gate
check: ## Full local gate: lint, format, types, imports, templates, migrations, security, tests
	$(RUN) sh -c '\
	  ruff check . && ruff format --check . && mypy apps config && lint-imports && \
	  djlint templates apps --check --quiet && djlint templates apps --lint --quiet && \
	  python manage.py makemigrations --check --dry-run && \
	  bandit -q -c pyproject.toml -r apps config && \
	  pytest -q -n auto --cov'
	scripts/fetch-vendor.sh --verify
lint: ## Lint only
	$(RUN) sh -c 'ruff check . && djlint templates apps --lint --quiet'
fmt: ## Format Python and templates
	$(RUN) sh -c 'ruff check --fix . ; ruff format . && djlint templates apps --reformat --quiet'
typecheck: ## mypy
	$(RUN) mypy apps config
test: ## Full test suite with coverage gate
	$(RUN) pytest -q -n auto --cov
test-fast: ## Tests without coverage, stop at first failure
	$(RUN) pytest -q -x -n auto

e2e: ## Playwright smoke against the running stack (needs: uv sync --group e2e && playwright install chromium)
	E2E_BASE_URL=http://localhost:8080 uv run --group e2e pytest tests/e2e -m e2e -p no:django -o addopts=""

# ------------------------------------------------------------------ assets
tools: ## Fetch the pinned Tailwind CLI (SHA-256 verified)
	scripts/fetch-tailwind.sh $(TAILWIND)
css: tools ## Build CSS
	$(TAILWIND) -i static/src/css/app.css -o static/dist/app.css --minify
css-watch: tools ## Rebuild CSS on change
	$(TAILWIND) -i static/src/css/app.css -o static/dist/app.css --watch
vendor-verify: ## Verify vendored JS against static/vendor/manifest.json
	scripts/fetch-vendor.sh --verify
messages: ## Extract and compile translation catalogues
	$(RUN) sh -c 'python manage.py makemessages -l en --ignore=.venv && python manage.py compilemessages'

image: ## Build the production image locally
	docker build -f docker/Dockerfile --target runtime -t rpl:local .
