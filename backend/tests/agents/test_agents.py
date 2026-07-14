"""Tests for LLM-backed agents, the mock provider, the factory, and the agent graph."""

from __future__ import annotations

import pytest

from app.agents.analysis_agents import DeploymentAnalysisAgent
from app.agents.control_agents import PlannerAgent
from app.agents.reasoning_agents import ReflectionAgent, RootCauseAgent
from app.agents.registry import build_agent_registry
from app.config.settings import Settings
from app.domain.enums import AgentName
from app.graphs.runner import InvestigationGraphRunner
from app.graphs.supervisor_graph import build_investigation_graph
from app.infrastructure.llm.factory import get_llm_provider
from app.infrastructure.llm.mock import MockLLMProvider, build_default_mock_responses
from app.state.investigation_state import build_initial_state

INCIDENT = build_initial_state(
    incident_id="INC-A-1",
    incident_description="Users cannot log in; auth API returns HTTP 500.",
    affected_service="auth-api",
)


def _llm() -> MockLLMProvider:
    return MockLLMProvider()


async def test_planner_agent_produces_plan() -> None:
    update = await PlannerAgent(_llm()).run(dict(INCIDENT))
    assert len(update["execution_plan"]) >= 5
    assert update["confidence_scores"][AgentName.PLANNER.value] == 1.0


async def test_deployment_agent_maps_deployments() -> None:
    update = await DeploymentAnalysisAgent(_llm()).run(dict(INCIDENT))
    assert update["deployments"][0]["version"] == "v2.4.0"
    # Enum-valued fields must serialize to their string values.
    assert isinstance(update["deployments"][0]["rollback_available"], bool)


async def test_root_cause_agent_ranks_and_scores() -> None:
    update = await RootCauseAgent(_llm()).run(dict(INCIDENT))
    cands = update["root_cause_candidates"]
    assert cands[0]["category"] == "bad_deployment"
    # Node confidence equals the leading hypothesis confidence.
    assert update["confidence_scores"][AgentName.ROOT_CAUSE.value] == 0.86


async def test_reflection_agent_increments_passes() -> None:
    state = dict(INCIDENT)
    state["reflection_passes"] = 1
    update = await ReflectionAgent(_llm()).run(state)
    assert update["reflection_passes"] == 2
    assert update["reflection_gaps"] == []  # mock reports sufficient=True


async def test_reflection_gaps_when_insufficient() -> None:
    responses = build_default_mock_responses()
    responses[AgentName.REFLECTION] = {
        "sufficient": False,
        "gaps": ["Need more metric coverage."],
        "confidence": 0.3,
    }
    update = await ReflectionAgent(MockLLMProvider(responses)).run(dict(INCIDENT))
    assert update["reflection_gaps"] == ["Need more metric coverage."]


async def test_mock_provider_raises_for_unregistered_agent() -> None:
    from app.domain.exceptions import LLMError
    from app.schemas.agent_io import PlannerOutput

    provider = MockLLMProvider(responses={})
    with pytest.raises(LLMError):
        await provider.structured_output(
            agent=AgentName.PLANNER,
            system_prompt="s",
            user_prompt="u",
            output_model=PlannerOutput,
        )


def test_factory_falls_back_to_mock_without_key() -> None:
    settings = Settings(llm_provider="anthropic", anthropic_api_key=None)
    provider = get_llm_provider(settings)
    assert provider.model_name == "mock-llm"


def test_factory_mock_provider() -> None:
    settings = Settings(llm_provider="mock")
    assert get_llm_provider(settings).model_name == "mock-llm"


async def test_full_graph_with_real_agents_reaches_approval() -> None:
    graph = build_investigation_graph(build_agent_registry(_llm()))
    runner = InvestigationGraphRunner(graph)
    state = await runner.start(dict(INCIDENT), thread_id="ag-1")

    assert state["alerts"] and state["logs"] and state["metrics"]
    assert state["deployments"] and state["dependencies"]
    assert state["timeline"] and state["root_cause_candidates"]
    assert state["recommendations"] and state["reports"]
    top = max(state["root_cause_candidates"], key=lambda c: c["confidence"])
    assert top["category"] == "bad_deployment"
    assert await runner.is_awaiting_approval(thread_id="ag-1")


async def test_full_graph_with_real_agents_resume_approved() -> None:
    graph = build_investigation_graph(build_agent_registry(_llm()))
    runner = InvestigationGraphRunner(graph)
    await runner.start(dict(INCIDENT), thread_id="ag-2")
    final = await runner.resume(thread_id="ag-2", approved=True)
    assert final["notifications"]
    assert "persist" in final["completed_nodes"]
