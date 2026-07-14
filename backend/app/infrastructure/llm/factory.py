"""LLM provider factory.

Selects a provider from settings, falling back to the mock provider whenever a real
provider cannot be configured (e.g. missing API key) so the platform always runs.
"""

from __future__ import annotations

from app.config.logging import get_logger
from app.config.settings import Settings, get_settings
from app.infrastructure.llm.base import LLMProvider
from app.infrastructure.llm.mock import MockLLMProvider

logger = get_logger(__name__)


def get_llm_provider(settings: Settings | None = None) -> LLMProvider:
    """Return the configured LLM provider.

    ``LLM_PROVIDER=mock`` (or a missing Anthropic key) yields the deterministic mock so the
    graph runs offline. ``LLM_PROVIDER=anthropic`` with a key yields the Anthropic provider.
    """
    settings = settings or get_settings()

    if settings.llm_provider == "mock":
        return MockLLMProvider()

    if settings.llm_provider == "anthropic":
        if not settings.anthropic_api_key:
            logger.warning("llm.fallback_to_mock", extra={"reason": "no_anthropic_api_key"})
            return MockLLMProvider()
        from app.infrastructure.llm.anthropic_provider import AnthropicLLMProvider

        return AnthropicLLMProvider(settings)

    logger.warning(
        "llm.unsupported_provider_uses_mock", extra={"provider": settings.llm_provider}
    )
    return MockLLMProvider()
