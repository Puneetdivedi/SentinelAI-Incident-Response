"""Unit tests for application settings validation and normalization."""

from __future__ import annotations

from app.config.settings import Settings


def test_app_env_is_normalized() -> None:
    settings = Settings(app_env="Production")
    assert settings.app_env == "production"


def test_debug_is_disabled_in_production() -> None:
    settings = Settings(app_env="production", app_debug=True)
    assert settings.app_debug is False
