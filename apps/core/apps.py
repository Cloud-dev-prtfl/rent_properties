from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "apps.core"
    label = "core"
    verbose_name = "Core platform"

    def ready(self) -> None:
        from apps.core.logging import configure_structlog  # noqa: PLC0415

        configure_structlog()
