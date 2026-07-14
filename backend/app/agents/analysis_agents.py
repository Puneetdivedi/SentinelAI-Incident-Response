"""Evidence-gathering agents run in parallel: Alert, Log, Metrics, Deployment, Dependency."""

from __future__ import annotations

from typing import Any

from app.agents.base import BaseAgent
from app.domain.enums import AgentName
from app.schemas.agent_io import (
    AlertAnalysisOutput,
    DependencyAnalysisOutput,
    DeploymentAnalysisOutput,
    LogAnalysisOutput,
    MetricsAnalysisOutput,
)
from app.state.investigation_state import InvestigationState


def _incident_context(state: InvestigationState) -> str:
    return (
        f"Incident: {state.get('incident_description')}\n"
        f"Affected service: {state.get('affected_service') or 'unknown'}"
    )


class AlertAnalysisAgent(BaseAgent):
    name = AgentName.ALERT_ANALYSIS
    output_model = AlertAnalysisOutput

    def build_user_prompt(self, state: InvestigationState) -> str:
        return f"{_incident_context(state)}\nIdentify firing alerts during the incident."

    def map_output(self, output: AlertAnalysisOutput, state: InvestigationState) -> dict[str, Any]:
        return {"alerts": [a.model_dump(mode="json") for a in output.alerts]}


class LogAnalysisAgent(BaseAgent):
    name = AgentName.LOG_ANALYSIS
    output_model = LogAnalysisOutput

    def build_user_prompt(self, state: InvestigationState) -> str:
        return f"{_incident_context(state)}\nExtract the most relevant log lines."

    def map_output(self, output: LogAnalysisOutput, state: InvestigationState) -> dict[str, Any]:
        return {"logs": [entry.model_dump(mode="json") for entry in output.logs]}


class MetricsAnalysisAgent(BaseAgent):
    name = AgentName.METRICS_ANALYSIS
    output_model = MetricsAnalysisOutput

    def build_user_prompt(self, state: InvestigationState) -> str:
        return f"{_incident_context(state)}\nAnalyze anomalous metrics during the incident."

    def map_output(self, output: MetricsAnalysisOutput, state: InvestigationState) -> dict[str, Any]:
        return {"metrics": [m.model_dump(mode="json") for m in output.metrics]}


class DeploymentAnalysisAgent(BaseAgent):
    name = AgentName.DEPLOYMENT_ANALYSIS
    output_model = DeploymentAnalysisOutput

    def build_user_prompt(self, state: InvestigationState) -> str:
        return f"{_incident_context(state)}\nIdentify deployments near the incident onset."

    def map_output(self, output: DeploymentAnalysisOutput, state: InvestigationState) -> dict[str, Any]:
        return {"deployments": [d.model_dump(mode="json") for d in output.deployments]}


class DependencyAnalysisAgent(BaseAgent):
    name = AgentName.DEPENDENCY_ANALYSIS
    output_model = DependencyAnalysisOutput

    def build_user_prompt(self, state: InvestigationState) -> str:
        return f"{_incident_context(state)}\nAssess dependency health."

    def map_output(self, output: DependencyAnalysisOutput, state: InvestigationState) -> dict[str, Any]:
        return {"dependencies": [d.model_dump(mode="json") for d in output.dependencies]}
