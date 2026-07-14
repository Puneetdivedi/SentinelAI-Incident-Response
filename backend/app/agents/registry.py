"""Assemble the LLM-backed agent registry and the default investigation graph.

Every agent's ``run`` method is a ``NodeFn``; this module instruments them exactly like the
baseline registry, so the supervisor graph is built the same way regardless of whether it is
running deterministic baseline nodes or real agents.
"""

from __future__ import annotations

from app.agents.analysis_agents import (
    AlertAnalysisAgent,
    DependencyAnalysisAgent,
    DeploymentAnalysisAgent,
    LogAnalysisAgent,
    MetricsAnalysisAgent,
)
from app.agents.control_agents import PlannerAgent, SupervisorAgent
from app.agents.reasoning_agents import (
    CorrelationAgent,
    HistoricalIncidentAgent,
    RecommendationAgent,
    ReflectionAgent,
    RootCauseAgent,
)
from app.agents.reporting_agents import IncidentReportAgent, NotificationAgent
from app.graphs.registry import NodeRegistry, build_registry
from app.infrastructure.llm.base import LLMProvider

_AGENT_CLASSES = [
    SupervisorAgent,
    PlannerAgent,
    AlertAnalysisAgent,
    LogAnalysisAgent,
    MetricsAnalysisAgent,
    DeploymentAnalysisAgent,
    DependencyAnalysisAgent,
    CorrelationAgent,
    HistoricalIncidentAgent,
    RootCauseAgent,
    ReflectionAgent,
    RecommendationAgent,
    IncidentReportAgent,
    NotificationAgent,
]


def build_agent_registry(llm: LLMProvider, *, max_retries: int = 2) -> NodeRegistry:
    """Instantiate every agent with the given LLM provider and return an instrumented registry."""
    raw = {}
    for agent_cls in _AGENT_CLASSES:
        agent = agent_cls(llm)
        raw[agent.name] = agent.run
    return build_registry(raw, max_retries=max_retries)
