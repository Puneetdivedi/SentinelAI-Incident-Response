"""Tests for data-source providers and LangChain tools."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.domain.exceptions import ToolExecutionError
from app.tools.analysis_tools import PythonExecutionTool, SqlQueryTool
from app.tools.base import build_langchain_tools
from app.tools.report_tools import (
    ChartGenerationTool,
    MarkdownReportTool,
    NotificationGeneratorTool,
    PdfReportTool,
    TimelineGeneratorTool,
    WordReportTool,
)
from app.tools.retrieval_tools import (
    DeploymentHistoryTool,
    IncidentSearchTool,
    LogSearchTool,
    MetricsQueryTool,
    VectorSearchTool,
)
from app.tools.toolset import build_all_tools, build_mock_providers


@pytest.fixture
def providers():
    return build_mock_providers()


# ── Retrieval tools ──────────────────────────────────────────
async def test_log_search_filters_by_service(providers) -> None:
    tool = LogSearchTool(providers.logs)
    results = await tool.arun(query="500 QueuePool", service="auth-api")
    assert results
    assert all(r["service"] == "auth-api" for r in results)


async def test_metrics_query_returns_series(providers) -> None:
    tool = MetricsQueryTool(providers.metrics)
    assert (await tool.arun(metric="db_connections"))[0]["value"] == 100.0


async def test_deployment_history_newest_first(providers) -> None:
    deployments = await DeploymentHistoryTool(providers.deployments).arun(service="auth-api")
    assert deployments[0]["version"] == "v2.4.0"


async def test_incident_search_ranks_by_similarity(providers) -> None:
    matches = await IncidentSearchTool(providers.incidents).arun(
        query="login auth pool connections deployment 500"
    )
    assert matches[0]["incident_id"] == "INC-2025-0421"
    assert "keywords" not in matches[0]


async def test_vector_search_returns_scored_docs(providers) -> None:
    docs = await VectorSearchTool(providers.vectors).arun(query="connection pool exhaustion login", k=3)
    assert docs[0]["id"] == "kb-pool"
    assert docs[0]["score"] > 0


# ── Analysis tools ───────────────────────────────────────────
async def test_python_exec_basic() -> None:
    out = await PythonExecutionTool().arun(code="result = sum([1, 2, 3]) * 2")
    assert out["result"] == 12


async def test_python_exec_blocks_import() -> None:
    with pytest.raises(ToolExecutionError):
        await PythonExecutionTool().arun(code="import os")


async def test_python_exec_blocks_dunder() -> None:
    with pytest.raises(ToolExecutionError):
        await PythonExecutionTool().arun(code="().__class__.__bases__")


async def test_sql_tool_rejects_writes() -> None:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    factory = async_sessionmaker(engine)
    tool = SqlQueryTool(factory)
    for bad in ("DELETE FROM users", "DROP TABLE users", "SELECT 1; DROP TABLE users"):
        with pytest.raises(ToolExecutionError):
            await tool.arun(query=bad)
    # A legitimate SELECT works.
    rows = await tool.arun(query="SELECT 42 AS answer")
    assert rows[0]["answer"] == 42
    await engine.dispose()


# ── Report tools ─────────────────────────────────────────────
async def test_markdown_report_contains_sections() -> None:
    md = await MarkdownReportTool().arun(
        title="INC-1 Report",
        executive_summary="Auth outage.",
        recommendations=["Roll back v2.4.0"],
    )
    assert "# INC-1 Report" in md
    assert "## Recommendations" in md
    assert "Roll back v2.4.0" in md


async def test_timeline_generator_sorts() -> None:
    events = [
        {"timestamp": "2026-07-14T09:00:00", "label": "alert"},
        {"timestamp": "2026-07-14T08:55:00", "label": "deploy"},
    ]
    timeline = await TimelineGeneratorTool().arun(events=events)
    assert timeline[0]["label"] == "deploy"


async def test_notification_generator_formats() -> None:
    note = await NotificationGeneratorTool().arun(
        incident_id="INC-1", status="investigating",
        probable_cause="bad deploy", next_steps="rollback",
    )
    assert note["channel"] == "slack"
    assert "INC-1" in note["message"]


async def test_pdf_report_produces_pdf_bytes() -> None:
    data = await PdfReportTool().arun(title="INC-1", content="# INC-1\n\n## Summary\nOutage.")
    assert data[:5] == b"%PDF-"


async def test_docx_report_produces_zip_bytes() -> None:
    data = await WordReportTool().arun(title="INC-1", content="# INC-1\n\n- item")
    # DOCX is a ZIP container.
    assert data[:2] == b"PK"


async def test_chart_generation_produces_png() -> None:
    png = await ChartGenerationTool().arun(
        title="DB connections", x=["08:55", "09:00"], y=[40.0, 100.0]
    )
    assert png[:8] == b"\x89PNG\r\n\x1a\n"


async def test_chart_generation_length_mismatch() -> None:
    with pytest.raises(ToolExecutionError):
        await ChartGenerationTool().arun(title="bad", x=["a"], y=[1.0, 2.0])


# ── Toolset / LangChain adapter ──────────────────────────────
def test_build_all_tools_and_langchain_adapter() -> None:
    tools = build_all_tools()
    names = {t.name for t in tools}
    assert {"log_search", "metrics_query", "python_exec", "markdown_report", "chart_generation"} <= names
    lc_tools = build_langchain_tools(tools)
    assert len(lc_tools) == len(tools)
    assert all(hasattr(t, "ainvoke") for t in lc_tools)


async def test_langchain_tool_invocation() -> None:
    providers = build_mock_providers()
    [lc_log] = build_langchain_tools([LogSearchTool(providers.logs)])
    result = await lc_log.ainvoke({"query": "QueuePool", "service": "auth-api"})
    assert result and result[0]["service"] == "auth-api"
