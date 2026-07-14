"""Reasoning agents: Correlation, Historical, Root Cause, Reflection, Recommendation."""

from __future__ import annotations

from typing import Any

from app.agents.base import BaseAgent, render_context
from app.domain.enums import AgentName
from app.schemas.agent_io import (
    CorrelationOutput,
    HistoricalOutput,
    RecommendationOutput,
    ReflectionOutput,
    RootCauseOutput,
)
from app.state.investigation_state import InvestigationState


class CorrelationAgent(BaseAgent):
    name = AgentName.CORRELATION
    output_model = CorrelationOutput

    def build_user_prompt(self, state: InvestigationState) -> str:
        context = render_context(state, ["alerts", "logs", "metrics", "deployments", "dependencies"])
        return f"Correlate the following evidence into a timeline:\n{context}"

    def map_output(self, output: CorrelationOutput, state: InvestigationState) -> dict[str, Any]:
        timeline = sorted(
            (e.model_dump(mode="json") for e in output.timeline),
            key=lambda e: e["timestamp"],
        )
        return {"timeline": timeline}


class HistoricalIncidentAgent(BaseAgent):
    name = AgentName.HISTORICAL_INCIDENT
    output_model = HistoricalOutput

    def build_user_prompt(self, state: InvestigationState) -> str:
        context = render_context(state, ["incident_description", "timeline"])
        return f"Find historical incidents similar to:\n{context}"

    def map_output(self, output: HistoricalOutput, state: InvestigationState) -> dict[str, Any]:
        return {"historical_matches": [m.model_dump(mode="json") for m in output.matches]}


class RootCauseAgent(BaseAgent):
    name = AgentName.ROOT_CAUSE
    output_model = RootCauseOutput

    def build_user_prompt(self, state: InvestigationState) -> str:
        context = render_context(
            state,
            ["timeline", "logs", "metrics", "deployments", "dependencies", "historical_matches"],
        )
        return f"Determine ranked root-cause hypotheses from:\n{context}"

    def map_output(self, output: RootCauseOutput, state: InvestigationState) -> dict[str, Any]:
        candidates = [c.model_dump(mode="json") for c in output.candidates]
        # Surface the leading hypothesis's confidence as this node's score.
        top = max(output.candidates, key=lambda c: c.confidence)
        return {
            "root_cause_candidates": candidates,
            "confidence_scores": {self.name.value: top.confidence},
        }


class ReflectionAgent(BaseAgent):
    name = AgentName.REFLECTION
    output_model = ReflectionOutput

    def build_user_prompt(self, state: InvestigationState) -> str:
        context = render_context(state, ["root_cause_candidates"])
        return (
            "Assess whether the evidence sufficiently supports the leading root cause. "
            f"If not, list specific gaps.\n{context}"
        )

    def map_output(self, output: ReflectionOutput, state: InvestigationState) -> dict[str, Any]:
        gaps = [] if output.sufficient else list(output.gaps)
        return {
            "reflection_gaps": gaps,
            "reflection_passes": state.get("reflection_passes", 0) + 1,
        }


class RecommendationAgent(BaseAgent):
    name = AgentName.RECOMMENDATION
    output_model = RecommendationOutput

    def build_user_prompt(self, state: InvestigationState) -> str:
        context = render_context(state, ["root_cause_candidates", "dependencies"])
        return f"Recommend prioritized remediation for:\n{context}"

    def map_output(self, output: RecommendationOutput, state: InvestigationState) -> dict[str, Any]:
        return {"recommendations": [r.model_dump(mode="json") for r in output.recommendations]}
