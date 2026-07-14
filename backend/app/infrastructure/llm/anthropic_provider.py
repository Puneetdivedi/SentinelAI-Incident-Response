"""Anthropic LLM provider.

Wraps LangChain's ``ChatAnthropic`` with structured output. ``langchain_anthropic`` is
imported lazily so the package is only required when this provider is actually used (the
mock provider has no such dependency).
"""

from __future__ import annotations

from app.config.logging import get_logger
from app.config.settings import Settings
from app.domain.enums import AgentName
from app.domain.exceptions import LLMError
from app.infrastructure.llm.base import LLMProvider, OutputT
from app.prompts.agent_prompts import PROMPT_VERSION

logger = get_logger(__name__)


class AnthropicLLMProvider(LLMProvider):
    def __init__(self, settings: Settings) -> None:
        if not settings.anthropic_api_key:
            raise LLMError("ANTHROPIC_API_KEY is not configured.")
        try:
            from langchain_anthropic import ChatAnthropic
        except ImportError as exc:  # pragma: no cover - depends on optional install
            raise LLMError(
                "langchain-anthropic is not installed; install it or use LLM_PROVIDER=mock."
            ) from exc

        self._settings = settings
        self._chat = ChatAnthropic(
            model=settings.llm_model,
            api_key=settings.anthropic_api_key,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
        )

    @property
    def model_name(self) -> str:
        return self._settings.llm_model

    async def structured_output(
        self,
        *,
        agent: AgentName,
        system_prompt: str,
        user_prompt: str,
        output_model: type[OutputT],
    ) -> OutputT:
        from langchain_core.messages import HumanMessage, SystemMessage

        structured = self._chat.with_structured_output(output_model)
        try:
            result = await structured.ainvoke(
                [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)],
                config={
                    "run_name": f"{agent.value}:{PROMPT_VERSION}",
                    "metadata": {"agent": agent.value, "prompt_version": PROMPT_VERSION},
                },
            )
        except Exception as exc:  # noqa: BLE001 - normalize to a domain error
            raise LLMError(f"Anthropic call failed for agent '{agent.value}': {exc}") from exc

        if not isinstance(result, output_model):
            raise LLMError(f"Anthropic returned an unexpected type for agent '{agent.value}'.")
        return result
