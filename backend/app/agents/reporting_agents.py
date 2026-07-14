"""Reporting agents: Incident Report and Notification."""

from __future__ import annotations

from typing import Any

from app.agents.base import BaseAgent, render_context
from app.domain.enums import AgentName
from app.schemas.agent_io import IncidentReportOutput, NotificationOutput
from app.state.investigation_state import InvestigationState


class IncidentReportAgent(BaseAgent):
    name = AgentName.INCIDENT_REPORT
    output_model = IncidentReportOutput

    def build_user_prompt(self, state: InvestigationState) -> str:
        context = render_context(
            state,
            ["incident_description", "timeline", "root_cause_candidates", "recommendations"],
        )
        return f"Write a Markdown incident report from:\n{context}"

    def map_output(self, output: IncidentReportOutput, state: InvestigationState) -> dict[str, Any]:
        return {
            "reports": [
                {
                    "format": "markdown",
                    "title": output.title,
                    "content": output.content_markdown,
                }
            ]
        }


class NotificationAgent(BaseAgent):
    name = AgentName.NOTIFICATION
    output_model = NotificationOutput

    def build_user_prompt(self, state: InvestigationState) -> str:
        context = render_context(state, ["incident_id", "root_cause_candidates", "recommendations"])
        approval = state.get("human_approval_status", "pending")
        return f"Draft a stakeholder notification (approval status: {approval}) for:\n{context}"

    def map_output(self, output: NotificationOutput, state: InvestigationState) -> dict[str, Any]:
        return {
            "notifications": [
                {
                    "channel": output.channel,
                    "audience": output.audience,
                    "message": output.message,
                }
            ]
        }
