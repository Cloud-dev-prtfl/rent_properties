import re
import uuid
from collections.abc import Callable

import structlog
from django.conf import settings
from django.http import HttpRequest, HttpResponse

from apps.core import health
from apps.core.clientip import get_client_ip
from apps.core.context import set_request_id

REQUEST_ID_HEADER = "X-Request-ID"
# Accept an upstream ID (platform router / proxy) only if it is short and safe to log.
_VALID_REQUEST_ID = re.compile(r"^[A-Za-z0-9._-]{8,64}$")


class HealthCheckMiddleware:
    """Serve health probes before ALLOWED_HOSTS checks and HTTPS redirects.

    Platform health checkers (Render, Fly.io, kamal-proxy, Traefik/Coolify) connect over plain
    HTTP with internal Host headers, which would otherwise get a 400 or a 301.
    """

    ROUTES: dict[str, Callable[[HttpRequest], HttpResponse]] = {
        "/healthz": health.healthz,
        "/readyz": health.readyz,
    }

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        view = self.ROUTES.get(request.path_info)
        if view is not None:
            return view(request)
        return self.get_response(request)


class ClientIPMiddleware:
    """Expose the real client IP as `request.client_ip` (see apps.core.clientip)."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request.client_ip = get_client_ip(request)  # type: ignore[attr-defined]
        return self.get_response(request)


class RequestContextMiddleware:
    """Assigns a request ID and binds it (and later the user) to every log line."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        incoming = request.headers.get(REQUEST_ID_HEADER, "")
        request_id = incoming if _VALID_REQUEST_ID.match(incoming) else uuid.uuid4().hex
        request.request_id = request_id  # type: ignore[attr-defined]
        set_request_id(request_id)
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)
        try:
            response = self.get_response(request)
        finally:
            set_request_id(None)
        response[REQUEST_ID_HEADER] = request_id
        return response

    def process_view(self, request: HttpRequest, *_args: object, **_kwargs: object) -> None:
        # Runs after AuthenticationMiddleware, so request.user is available here.
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated:
            structlog.contextvars.bind_contextvars(user_public_id=str(user.public_id))


class SecurityHeadersMiddleware:
    """Headers Django does not set itself (US-015)."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        response.setdefault("Permissions-Policy", settings.PERMISSIONS_POLICY)
        return response
