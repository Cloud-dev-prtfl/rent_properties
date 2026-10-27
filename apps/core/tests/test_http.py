"""Shell page, error pages, security headers, request IDs and health endpoints."""

import pytest
import structlog
from django.test import Client, RequestFactory

from apps.accounts.tests.factories import UserFactory
from apps.core import health, views
from apps.core.middleware import RequestContextMiddleware

pytestmark = pytest.mark.django_db


def test_home_renders_accessible_shell(client):
    response = client.get("/")
    html = response.content.decode()
    assert response.status_code == 200
    assert 'lang="en"' in html
    assert 'dir="ltr"' in html
    assert 'href="#main"' in html  # skip link
    assert '<main id="main"' in html
    assert '<nav aria-label="Main">' in html
    assert 'aria-current="page"' in html
    assert 'role="status"' in html
    assert 'aria-live="polite"' in html
    assert 'role="alert"' in html


def test_security_headers_are_set(client):
    response = client.get("/")
    assert response["X-Content-Type-Options"] == "nosniff"
    assert response["X-Frame-Options"] == "DENY"
    assert response["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "camera=()" in response["Permissions-Policy"]
    csp = response["Content-Security-Policy"]
    assert "default-src 'self'" in csp
    assert "frame-ancestors 'none'" in csp
    assert "unsafe-inline" not in csp


def test_request_id_is_generated_and_returned(client):
    response = client.get("/")
    assert len(response["X-Request-ID"]) == 32


def test_valid_upstream_request_id_is_propagated(client):
    response = client.get("/", HTTP_X_REQUEST_ID="alb-trace-0001")
    assert response["X-Request-ID"] == "alb-trace-0001"


def test_unsafe_upstream_request_id_is_replaced(client):
    response = client.get("/", HTTP_X_REQUEST_ID="bad id\nwith newline")
    assert response["X-Request-ID"] != "bad id\nwith newline"


def test_authenticated_user_is_bound_to_log_context():
    user = UserFactory()
    request = RequestFactory().get("/")
    request.user = user
    RequestContextMiddleware(lambda r: None).process_view(request, views.home, (), {})
    assert structlog.contextvars.get_contextvars()["user_public_id"] == str(user.public_id)
    structlog.contextvars.clear_contextvars()


def test_unknown_page_uses_custom_404(client):
    response = client.get("/no-such-page/")
    assert response.status_code == 404
    assert "Page not found" in response.content.decode()


def test_csrf_failure_uses_friendly_page():
    client = Client(enforce_csrf_checks=True)
    response = client.post("/")
    assert response.status_code == 403
    assert "Your session has expired" in response.content.decode()


@pytest.mark.parametrize(
    ("handler", "status", "text"),
    [
        (views.bad_request, 400, "Bad request"),
        (views.permission_denied, 403, "Access denied"),
        (views.page_not_found, 404, "Page not found"),
    ],
)
def test_error_handlers(rf, handler, status, text):
    response = handler(rf.get("/"), Exception())
    assert response.status_code == status
    assert text in response.content.decode()


def test_server_error_page_shows_request_id(rf):
    request = rf.get("/")
    request.request_id = "abc123def456"
    response = views.server_error(request)
    assert response.status_code == 500
    assert "abc123def456" in response.content.decode()


def test_healthz_is_always_ok(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readyz_reports_each_dependency(client):
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "checks": {"database": "ok", "cache": "ok", "broker": "ok"},
    }


def test_readyz_returns_503_when_a_dependency_fails(client, monkeypatch):
    def broken() -> None:
        raise ConnectionError("down")

    monkeypatch.setitem(health.CHECKS, "broker", broken)
    response = client.get("/readyz")
    assert response.status_code == 503
    assert response.json()["checks"]["broker"] == "error"


def test_cache_check_detects_a_silently_failing_cache(monkeypatch):
    class SilentCache:
        def set(self, *args, **kwargs):
            return None

        def get(self, *args, **kwargs):
            return None

    monkeypatch.setattr(health, "caches", {"default": SilentCache()})
    with pytest.raises(ConnectionError):
        health.check_cache()


def test_health_endpoints_reject_post(client):
    assert client.post("/healthz").status_code == 405
