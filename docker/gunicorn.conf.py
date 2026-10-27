"""Gunicorn configuration for the web service (sync workers; the app is I/O-light per request)."""

import os

# Every PaaS injects PORT; self-hosted proxies target 8000.
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
workers = int(os.environ.get("WEB_CONCURRENCY", "3"))
threads = 1
timeout = 30
graceful_timeout = 30
keepalive = 75  # longer than typical proxy idle timeouts (60 s), avoids 502s on reused connections
max_requests = 1000
max_requests_jitter = 100
worker_tmp_dir = "/dev/shm"  # noqa: S108 — tmpfs heartbeat files, avoids disk stalls
accesslog = "-"
errorlog = "-"
# Trust X-Forwarded-Proto from the platform router / reverse proxy. Use "*" only where the
# container is reachable solely through that proxy (true on every supported target).
forwarded_allow_ips = os.environ.get("FORWARDED_ALLOW_IPS", "127.0.0.1")
