from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET


@require_GET
def home(request: HttpRequest) -> HttpResponse:
    # M0 shell page; replaced by the search home page in M3.
    return render(request, "core/home.html")


def bad_request(request: HttpRequest, exception: Exception | None = None) -> HttpResponse:
    return render(request, "errors/400.html", status=400)


def permission_denied(request: HttpRequest, exception: Exception | None = None) -> HttpResponse:
    return render(request, "errors/403.html", status=403)


def page_not_found(request: HttpRequest, exception: Exception | None = None) -> HttpResponse:
    return render(request, "errors/404.html", status=404)


def server_error(request: HttpRequest) -> HttpResponse:
    # Rendered without the full layout context: the failure may be in a context processor.
    return render(
        request,
        "errors/500.html",
        {"request_id": getattr(request, "request_id", "")},
        status=500,
    )


def csrf_failure(request: HttpRequest, reason: str = "") -> HttpResponse:
    return render(request, "errors/csrf_failure.html", status=403)
