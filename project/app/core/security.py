"""Security helpers: API key verification and input sanitization."""

from __future__ import annotations

import hmac
from typing import Optional

import bleach
from fastapi import Depends, Header, HTTPException, Request, status
from slowapi.util import get_remote_address

from app.core.config import Settings, get_settings


ALLOWED_TEXT_TAGS: list[str] = []
ALLOWED_TEXT_ATTRIBUTES: dict[str, list[str]] = {}


def sanitize_text(value: str) -> str:
    """Strip unwanted HTML/script content from text inputs."""
    cleaned = bleach.clean(
        value,
        tags=ALLOWED_TEXT_TAGS,
        attributes=ALLOWED_TEXT_ATTRIBUTES,
        strip=True,
    )
    return " ".join(cleaned.split())


def get_rate_limit_key(request: Request) -> str:
    """Build a rate-limit key from client IP and optional user identifier.

    OWASP API4 guidance recommends request throttling keyed to caller identity.
    """
    ip = get_remote_address(request)
    user_hint = request.headers.get("X-User-Id", "anonymous")
    return f"{ip}:{user_hint}"


def _constant_time_match(candidate: str, expected: str) -> bool:
    return hmac.compare_digest(candidate.encode("utf-8"), expected.encode("utf-8"))


def verify_api_key(
    request: Request,
    api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    settings: Settings = Depends(get_settings),
) -> None:
    """Validate API key from header against env-provided active key set.

    - No hardcoded secrets.
    - Supports key rotation by accepting multiple active keys.
    """
    # Allow runtime-configurable header name while keeping dependency signature explicit.
    header_name = settings.api_key_header
    incoming_key = api_key or request.headers.get(header_name)

    if not settings.active_api_keys:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API keys are not configured on the server.",
        )

    if not incoming_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key.",
        )

    active_keys = [secret.get_secret_value() for secret in settings.active_api_keys]
    if not any(_constant_time_match(incoming_key, key) for key in active_keys):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )
