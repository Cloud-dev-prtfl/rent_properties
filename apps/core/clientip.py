"""Resolve the real client IP behind PaaS routers and reverse proxies (ADR-0014).

REMOTE_ADDR is the nearest proxy on every supported platform, so rate limits and audit records
need the address the trusted edge saw. Only headers from trusted hops are believed; anything a
client could forge (the left part of X-Forwarded-For) is ignored.
"""

import ipaddress

from django.conf import settings
from django.http import HttpRequest


def _valid_ip(value: str) -> str | None:
    candidate = value.strip()
    try:
        return str(ipaddress.ip_address(candidate))
    except ValueError:
        return None


def get_client_ip(request: HttpRequest) -> str | None:
    remote_addr: str | None = request.META.get("REMOTE_ADDR")

    header = settings.CLIENT_IP_HEADER
    if header:
        found = _valid_ip(request.headers.get(header, ""))
        return found or remote_addr

    hops = settings.TRUSTED_PROXY_COUNT
    forwarded = request.headers.get("X-Forwarded-For", "")
    if hops > 0 and forwarded:
        chain = [part for part in forwarded.split(",") if part.strip()]
        if len(chain) >= hops:
            # Each trusted proxy appends the address it received from; the entry added by the
            # outermost trusted proxy is the client.
            return _valid_ip(chain[-hops]) or remote_addr
    return remote_addr
