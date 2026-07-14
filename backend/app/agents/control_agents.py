"""Control-plane agents: Supervisor and Planner."""

from __future__ import annotations

from typing import Any

from app.agents.base import BaseAgent
from app.domain.enums import AgentName
from app.schemas.agent_io import PlannerOutput, SupervisorOutput
from app.state.investigation_state import InvestigationState


class SupervisorAgent(BaseAgent):
    name = AgentName.SUPERVISOR
    output_model = SupervisorOutput

    def build_user_prompt(self, state: InvestigationState) -> str:
        return (
            f"Incident {state.get('incident_id')}: {state.get('incident_description')}\n"
            f"Affected service: {state.get('affected_service') or 'unknown'}\n"
            "Acknowledge and start the investigation."
        )

    def map_output(self, output: SupervisorOutput, state: InvestigationState) -> dict[str, Any]:
        return {}


class PlannerAgent(BaseAgent):
    name = AgentName.PLANNER
    output_model = PlannerOutput

    def build_user_prompt(self, state: InvestigationState) -> str:
        return (
            f"Incident: {state.get('incident_description')}\n"
            f"Affected service: {state.get('affected_service') or 'unknown'}\n"
            "Produce an ordered investigation plan."
        )

    def map_output(self, output: PlannerOutput, state: InvestigationState) -> dict[str, Any]:
        return {"execution_plan": list(output.steps)}
