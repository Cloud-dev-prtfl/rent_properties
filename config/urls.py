"""Root URL map. Namespaces and mounts follow docs/architecture/03-codebase-structure.md §7."""

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path

from apps.core import health

# Outside i18n: machine endpoints and the ops console.
urlpatterns = [
    path("healthz", health.healthz, name="healthz"),
    path("readyz", health.readyz, name="readyz"),
    path("i18n/", include("django.conf.urls.i18n")),
    path(settings.ADMIN_URL_PREFIX, admin.site.urls),
]

# User-facing pages: English has no prefix, future languages get /<lang>/.
urlpatterns += i18n_patterns(
    path("", include("apps.core.urls")),
    prefix_default_language=False,
)

handler400 = "apps.core.views.bad_request"
handler403 = "apps.core.views.permission_denied"
handler404 = "apps.core.views.page_not_found"
handler500 = "apps.core.views.server_error"
