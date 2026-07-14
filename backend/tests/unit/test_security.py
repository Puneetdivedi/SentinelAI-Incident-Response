"""Unit tests for password hashing and JWT helpers (no DB, no network)."""

from __future__ import annotations

import pytest

from app.config.settings import Settings
from app.domain.exceptions import AuthenticationError
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)

settings = Settings(jwt_secret_key="unit-test-secret")


def test_password_hash_roundtrip() -> None:
    hashed = hash_password("s3cret-pw")
    assert hashed != "s3cret-pw"
    assert verify_password("s3cret-pw", hashed) is True
    assert verify_password("wrong", hashed) is False


def test_access_token_roundtrip() -> None:
    token = create_access_token(settings, subject="u1", role="sre")
    claims = decode_token(settings, token, expected_type="access")
    assert claims.subject == "u1"
    assert claims.role == "sre"
    assert claims.token_type == "access"


def test_refresh_token_type_enforced() -> None:
    refresh = create_refresh_token(settings, subject="u1", role="admin")
    # Decoding a refresh token as an access token must fail.
    with pytest.raises(AuthenticationError):
        decode_token(settings, refresh, expected_type="access")
    # But decoding it as a refresh token succeeds.
    claims = decode_token(settings, refresh, expected_type="refresh")
    assert claims.token_type == "refresh"


def test_tampered_token_rejected() -> None:
    token = create_access_token(settings, subject="u1", role="viewer")
    with pytest.raises(AuthenticationError):
        decode_token(settings, token + "tampered", expected_type="access")


def test_wrong_secret_rejected() -> None:
    token = create_access_token(settings, subject="u1", role="viewer")
    other = Settings(jwt_secret_key="a-different-secret")
    with pytest.raises(AuthenticationError):
        decode_token(other, token)
