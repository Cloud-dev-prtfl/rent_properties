import structlog

from apps.core import logging as core_logging
from apps.core import telemetry


def test_redaction_masks_sensitive_keys():
    event = {"event": "signup", "email": "a@b.com", "Password": "x", "user_public_id": "u-1"}
    result = core_logging.redact_sensitive(None, "info", event)
    assert result["email"] == core_logging.REDACTED
    assert result["Password"] == core_logging.REDACTED
    assert result["user_public_id"] == "u-1"


def test_trace_context_is_omitted_without_an_active_span():
    assert "trace_id" not in core_logging.add_trace_context(None, "info", {"event": "x"})


def test_logging_config_selects_renderer():
    json_cfg = core_logging.build_logging_config(level="INFO", json=True)
    console_cfg = core_logging.build_logging_config(level="DEBUG", json=False)
    assert isinstance(
        json_cfg["formatters"]["structured"]["processors"][-1], structlog.processors.JSONRenderer
    )
    assert console_cfg["root"]["level"] == "DEBUG"


def test_sentry_scrubber_drops_cookies_and_redacts_fields():
    event = {
        "request": {
            "cookies": {"sessionid": "secret"},
            "headers": {"Authorization": "Bearer x", "Accept": "text/html"},
            "data": {"password": "pw", "title": "flat"},
        }
    }
    scrubbed = telemetry.scrub_event(event, None)
    assert "cookies" not in scrubbed["request"]
    assert scrubbed["request"]["headers"]["Authorization"] == "[REDACTED]"
    assert scrubbed["request"]["headers"]["Accept"] == "text/html"
    assert scrubbed["request"]["data"] == {"password": "[REDACTED]", "title": "flat"}


def test_configure_telemetry_initialises_sentry_once(monkeypatch, settings):
    calls: list[dict] = []
    monkeypatch.setattr(telemetry, "_configured", set())
    monkeypatch.setattr("sentry_sdk.init", lambda **kw: calls.append(kw))
    monkeypatch.setattr("sentry_sdk.set_tag", lambda *a: None)
    settings.SENTRY_DSN = "https://key@example.invalid/1"
    settings.OTEL_ENABLED = False

    telemetry.configure_telemetry(service_role="web")
    telemetry.configure_telemetry(service_role="web")

    assert len(calls) == 1
    assert calls[0]["send_default_pii"] is False
    assert calls[0]["before_send"] is telemetry.scrub_event


def test_configure_telemetry_without_dsn_is_a_noop(monkeypatch, settings):
    monkeypatch.setattr(telemetry, "_configured", set())
    settings.SENTRY_DSN = ""
    settings.OTEL_ENABLED = False
    telemetry.configure_telemetry(service_role="worker")
