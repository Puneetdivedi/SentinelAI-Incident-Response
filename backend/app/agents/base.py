"""Base agent.

Each agent binds a system prompt + a structured-output schema, builds a user prompt from
the current state, calls the LLM provider, and maps the validated output to a partial state
update. Retries, latency capture, error recording, and node bookkeeping are added by the
graph's ``instrument`` wrapper, so agents stay focused on prompt + mapping.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from app.domain.enums import AgentName
from app.infrastructure.llm.base import LLMProvider
from app.prompts.agent_prompts import get_system_prompt
from app.state.investigation_state import InvestigationState


def render_context(state: InvestigationState, keys: list[str]) -> str:
    """Render selected state keys as compact JSON for embedding in a prompt."""
    context = {key: state.get(key) for key in keys if state.get(key)}
    return json.dumps(context, indent=2, default=str)


class BaseAgent(ABC):
    #: Set by each concrete agent.
    name: AgentName
    output_model: type[BaseModel]

    def __init__(self, llm: LLMProvider) -> None:
        self._llm = llm

    @property
    def system_prompt(self) -> str:
        return get_system_prompt(self.name)

    @abstractmethod
    def build_user_prompt(self, state: InvestigationState) -> str:
        """Render the user prompt from the current investigation state."""

    @abstractmethod
    def map_output(self, output: Any, state: InvestigationState) -> dict[str, Any]:
        """Translate the validated LLM output into a partial state update."""

    async def run(self, state: InvestigationState) -> dict[str, Any]:
        output = await self._llm.structured_output(
            agent=self.name,
            system_prompt=self.system_prompt,
            user_prompt=self.build_user_prompt(state),
            output_model=self.output_model,
        )
        update = self.map_output(output, state)
        confidence = float(getattr(output, "confidence", 1.0))
        scores = dict(update.get("confidence_scores", {}))
        scores[self.name.value] = confidence
        update["confidence_scores"] = scores
        return update
