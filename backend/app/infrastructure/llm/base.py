"""LLM provider interface (port).

Agents depend only on this abstraction. It exposes a single ``structured_output`` method
that returns a validated Pydantic model, which is exactly the contract every agent needs
(agents always emit structured output). Concrete providers: Anthropic and a deterministic
mock. New providers (OpenAI, Gateway) implement the same interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

from app.domain.enums import AgentName

OutputT = TypeVar("OutputT", bound=BaseModel)


class LLMProvider(ABC):
    """Port for structured LLM generation."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Identifier of the underlying model (for observability)."""

    @abstractmethod
    async def structured_output(
        self,
        *,
        agent: AgentName,
        system_prompt: str,
        user_prompt: str,
        output_model: type[OutputT],
    ) -> OutputT:
        """Generate a response validated against ``output_model``.

        ``agent`` is passed for observability and to let mock/scripted providers return
        agent-appropriate fixtures. Implementations must raise ``LLMError`` on failure.
        """
