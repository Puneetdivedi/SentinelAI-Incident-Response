"""Security primitives: password hashing and JWT encode/decode.

Pure, dependency-injected helpers with no FastAPI or DB coupling, so they are trivially
unit-testable. Token claims follow RFC 7519 (sub, exp, iat, jti) plus custom ``role`` and
``type`` claims to distinguish access from refresh tokens.
"""

from __future__ import annotations

import base64
import hashlib
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

import bcrypt
from jose import JWTError, jwt

from app.config.settings import Settings
from app.domain.exceptions import AuthenticationError

TokenType = Literal["access", "refresh"]


def _prehash(plain_password: str) -> bytes:
    """SHA-256 + base64 pre-hash.

    bcrypt silently truncates anything past 72 bytes (and modern releases raise). Hashing
    to a fixed 44-byte base64 digest first removes that limit entirely and is a standard,
    safe construction (equivalent to passlib's ``bcrypt_sha256``).
    """
    digest = hashlib.sha256(plain_password.encode("utf-8")).digest()
    return base64.b64encode(digest)


def hash_password(plain_password: str) -> str:
    """Return a bcrypt hash of the given password."""
    return bcrypt.hashpw(_prehash(plain_password), bcrypt.gensalt()).decode("ascii")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Constant-time verification of a password against its hash."""
    try:
        return bcrypt.checkpw(
            _prehash(plain_password), hashed_password.encode("ascii")
        )
    except (ValueError, TypeError):
        return False


# A real, precomputed hash used only to equalize timing on unknown-user login paths.
DUMMY_PASSWORD_HASH = hash_password("sentinelai-timing-equalizer")


@dataclass(frozen=True, slots=True)
class TokenClaims:
    """Decoded and validated token claims."""

    subject: str
    role: str
    token_type: TokenType
    jti: str
    expires_at: datetime


def _create_token(
    *,
    settings: Settings,
    subject: str,
    role: str,
    token_type: TokenType,
    expires_delta: timedelta,
    now: datetime,
) -> str:
    expire = now + expires_delta
    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(
    settings: Settings, subject: str, role: str, *, now: datetime | None = None
) -> str:
    """Create a short-lived access token."""
    now = now or datetime.now(timezone.utc)
    return _create_token(
        settings=settings,
        subject=subject,
        role=role,
        token_type="access",
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        now=now,
    )


def create_refresh_token(
    settings: Settings, subject: str, role: str, *, now: datetime | None = None
) -> str:
    """Create a long-lived refresh token."""
    now = now or datetime.now(timezone.utc)
    return _create_token(
        settings=settings,
        subject=subject,
        role=role,
        token_type="refresh",
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
        now=now,
    )


def decode_token(
    settings: Settings, token: str, *, expected_type: TokenType | None = None
) -> TokenClaims:
    """Decode and validate a JWT.

    Raises ``AuthenticationError`` on any signature/expiry/type mismatch.
    """
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
    except JWTError as exc:  # signature invalid, expired, malformed
        raise AuthenticationError("Invalid or expired token.") from exc

    subject = payload.get("sub")
    role = payload.get("role")
    token_type = payload.get("type")
    jti = payload.get("jti")
    exp = payload.get("exp")

    if not subject or not role or token_type not in ("access", "refresh") or not jti:
        raise AuthenticationError("Malformed token claims.")

    if expected_type is not None and token_type != expected_type:
        raise AuthenticationError(
            f"Expected a {expected_type} token but received a {token_type} token."
        )

    return TokenClaims(
        subject=subject,
        role=role,
        token_type=token_type,  # type: ignore[arg-type]
        jti=jti,
        expires_at=datetime.fromtimestamp(exp, tz=timezone.utc),
    )
