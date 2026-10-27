"""Behaviour needed to run on every hosting target (ADR-0014)."""

import pytest
from django.core.management import call_command

from apps.core import audit
from apps.core.clientip import get_client_ip

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    ("header", "hops", "meta", "expected"),
    [
        # No proxy configuration: the socket peer.
        ("", 0, {"HTTP_X_FORWARDED_FOR": "6.6.6.6"}, "10.0.0.2"),
        # One trusted proxy (Heroku/Render router, kamal-proxy, Traefik, Caddy): the client
        # cannot spoof its address by sending its own X-Forwarded-For.
        ("", 1, {"HTTP_X_FORWARDED_FOR": "6.6.6.6, 203.0.113.9"}, "203.0.113.9"),
        # Two trusted hops (Cloudflare in front of a PaaS router).
        ("", 2, {"HTTP_X_FORWARDED_FOR": "203.0.113.9, 172.70.1.1"}, "203.0.113.9"),
        # Fewer entries than trusted hops: fall back to the peer.
        ("", 2, {"HTTP_X_FORWARDED_FOR": "203.0.113.9"}, "10.0.0.2"),
        # Garbage in the chain: fall back to the peer.
        ("", 1, {"HTTP_X_FORWARDED_FOR": "not-an-ip"}, "10.0.0.2"),
        # Platform header (Fly-Client-IP / CF-Connecting-IP), IPv6 normalised.
        ("Fly-Client-IP", 0, {"HTTP_FLY_CLIENT_IP": "2001:DB8::1"}, "2001:db8::1"),
        ("Fly-Client-IP", 0, {}, "10.0.0.2"),
    ],
)
def test_client_ip_resolution(rf, settings, header, hops, meta, expected):
    settings.CLIENT_IP_HEADER = header
    settings.TRUSTED_PROXY_COUNT = hops
    request = rf.get("/", REMOTE_ADDR="10.0.0.2", **meta)
    assert get_client_ip(request) == expected


def test_client_ip_is_exposed_on_requests_and_used_by_audit(client, settings, rf):
    settings.TRUSTED_PROXY_COUNT = 1
    response = client.get("/", HTTP_X_FORWARDED_FOR="198.51.100.4")
    assert response.wsgi_request.client_ip == "198.51.100.4"

    request = rf.get("/", REMOTE_ADDR="10.0.0.2")
    request.client_ip = "198.51.100.4"
    assert audit.record(action="x.y", request=request).ip == "198.51.100.4"


@pytest.mark.parametrize("path", ["/healthz", "/readyz"])
def test_health_probes_ignore_allowed_hosts(client, settings, path):
    # Platform checkers use internal hostnames that are not in ALLOWED_HOSTS.
    settings.ALLOWED_HOSTS = ["www.example.com"]
    response = client.get(path, HTTP_HOST="10.1.2.3:8000")
    assert response.status_code == 200


def test_other_paths_still_enforce_allowed_hosts(client, settings):
    settings.ALLOWED_HOSTS = ["www.example.com"]
    assert client.get("/", HTTP_HOST="evil.example.net").status_code == 400


def test_health_probes_are_not_redirected_to_https(client, settings):
    settings.SECURE_SSL_REDIRECT = True
    assert client.get("/healthz").status_code == 200
    assert client.get("/").status_code == 301


def test_release_command_applies_migrations_under_lock(capsys):
    call_command("release")
    out = capsys.readouterr().out
    assert "waiting for the release lock" in out
    assert "No migrations to apply" in out
    assert "release: done" in out
