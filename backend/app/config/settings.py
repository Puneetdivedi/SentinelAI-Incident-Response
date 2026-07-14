"""Application configuration.

A single, strongly-typed ``Settings`` object loaded from environment variables / ``.env``
using pydantic-settings (Pydantic v2). Grouped by concern and cached as a singleton via
``get_settings()`` so it can be injected anywhere (including FastAPI ``Depends``).
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Root settings object. All values overridable via environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────
    app_name: str = "SentinelAI"
    app_env: Literal["development", "staging", "production"] = "development"
    app_debug: bool = True
    api_v1_prefix: str = "/api/v1"
    backend_cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    # ── Security / JWT ───────────────────────────────────────
    jwt_secret_key: str = "change-me-to-a-long-random-string"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    rate_limit_per_minute: int = 120

    # ── PostgreSQL ───────────────────────────────────────────
    database_url: str = (
        "postgresql+asyncpg://sentinel:sentinel@localhost:5432/sentinelai"
    )

    # ── Redis ────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── Qdrant ───────────────────────────────────────────────
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_collection: str = "incident_knowledge"

    # ── LLM Provider ─────────────────────────────────────────
    llm_provider: Literal["anthropic", "openai", "gateway", "mock"] = "anthropic"
    llm_model: str = "claude-opus-4-8"
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None
    llm_temperature: float = 0.1
    llm_max_tokens: int = 4096

    # ── LangFuse ─────────────────────────────────────────────
    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None
    langfuse_host: str = "https://cloud.langfuse.com"

    # ── OpenTelemetry ────────────────────────────────────────
    otel_exporter_otlp_endpoint: str | None = "http://localhost:4317"
    otel_service_name: str = "sentinelai-backend"

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def _split_cors(cls, value: str | list[str]) -> list[str]:
        """Allow a comma-separated string in the env file."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def langfuse_enabled(self) -> bool:
        return bool(self.langfuse_public_key and self.langfuse_secret_key)

    @property
    def sync_database_url(self) -> str:
        """Sync DSN for Alembic (swaps the asyncpg driver for psycopg)."""
        return self.database_url.replace("+asyncpg", "+psycopg")


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton ``Settings`` instance."""
    return Settings()
