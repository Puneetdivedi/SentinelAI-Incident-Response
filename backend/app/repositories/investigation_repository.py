"""SQLAlchemy implementation of the investigation repository.

``save_state`` snapshots a LangGraph investigation state into the relational model: JSON
evidence columns on the investigation row, plus child rows for root causes, recommendations,
reports, and per-agent runs (rebuilt each save so a resume reflects the latest state).
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities import Investigation, Recommendation, Report, RootCauseHypothesis
from app.domain.enums import (
    AgentName,
    ApprovalStatus,
    InvestigationStatus,
    RecommendationPriority,
    ReportFormat,
    RemediationAction,
    RiskLevel,
    RootCauseCategory,
)
from app.domain.exceptions import EntityNotFoundError
from app.domain.value_objects import ConfidenceScore, Evidence
from app.models.investigation import (
    AgentRunModel,
    InvestigationModel,
    RecommendationModel,
    RootCauseModel,
)
from app.models.report import ReportModel
from app.repositories.interfaces import InvestigationRepository


class SqlAlchemyInvestigationRepository(InvestigationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, *, incident_id: str) -> Investigation:
        row = InvestigationModel(
            incident_id=incident_id,
            status=InvestigationStatus.PENDING,
            approval_status=ApprovalStatus.PENDING,
        )
        self._session.add(row)
        await self._session.flush()
        entity = await self.get(row.id)
        assert entity is not None
        return entity

    async def get(self, investigation_id: str) -> Investigation | None:
        result = await self._session.execute(
            select(InvestigationModel)
            .where(InvestigationModel.id == investigation_id)
            .options(
                selectinload(InvestigationModel.root_causes),
                selectinload(InvestigationModel.recommendations),
                selectinload(InvestigationModel.reports),
                selectinload(InvestigationModel.agent_runs),
            )
        )
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row is not None else None

    async def list(
        self, *, incident_id: str | None = None, limit: int = 50, offset: int = 0
    ) -> list[Investigation]:
        stmt = select(InvestigationModel).order_by(InvestigationModel.created_at.desc())
        if incident_id is not None:
            stmt = stmt.where(InvestigationModel.incident_id == incident_id)
        result = await self._session.execute(
            stmt.options(
                selectinload(InvestigationModel.root_causes),
                selectinload(InvestigationModel.recommendations),
                selectinload(InvestigationModel.reports),
            ).limit(limit).offset(offset)
        )
        return [self._to_entity(row) for row in result.scalars().all()]

    async def save_state(
        self,
        investigation_id: str,
        state: dict,
        *,
        status: InvestigationStatus,
        approval_status: ApprovalStatus,
        completed: bool = False,
        approved_by: str | None = None,
    ) -> Investigation:
        row = await self._session.get(InvestigationModel, investigation_id)
        if row is None:
            raise EntityNotFoundError(f"Investigation '{investigation_id}' not found.")

        # JSON evidence / bookkeeping columns.
        row.execution_plan = list(state.get("execution_plan", []))
        row.logs = list(state.get("logs", []))
        row.alerts = list(state.get("alerts", []))
        row.metrics = list(state.get("metrics", []))
        row.deployments = list(state.get("deployments", []))
        row.dependencies = list(state.get("dependencies", []))
        row.timeline = list(state.get("timeline", []))
        row.historical_match_ids = [
            m.get("incident_id") for m in state.get("historical_matches", []) if m.get("incident_id")
        ]
        row.confidence_scores = dict(state.get("confidence_scores", {}))
        row.errors = list(state.get("errors", []))
        row.langfuse_trace_id = state.get("langfuse_trace_id")
        row.langfuse_session_id = state.get("langfuse_session_id")

        row.status = status
        row.approval_status = approval_status
        if approved_by:
            row.approved_by = approved_by
        if completed:
            row.completed_at = datetime.now(timezone.utc)

        await self._replace_children(row, state)
        await self._session.flush()
        self._session.expire(row)
        return await self.get(investigation_id)  # reload with children

    def _to_entity(self, row: InvestigationModel | None) -> Investigation | None:
        if row is None:
            return None

        return Investigation(
            id=row.id,
            incident_id=row.incident_id,
            status=row.status,
            approval_status=row.approval_status,
            execution_plan=row.execution_plan or [],
            logs=row.logs or [],
            alerts=row.alerts or [],
            metrics=row.metrics or [],
            deployments=row.deployments or [],
            dependencies=row.dependencies or [],
            timeline=row.timeline or [],
            historical_match_ids=row.historical_match_ids or [],
            root_cause_candidates=[self._to_root_cause(rc) for rc in row.root_causes],
            recommendations=[self._to_recommendation(r) for r in row.recommendations],
            reports=[self._to_report(rp) for rp in row.reports],
            confidence_scores=row.confidence_scores or {},
            errors=row.errors or [],
            langfuse_trace_id=row.langfuse_trace_id,
            langfuse_session_id=row.langfuse_session_id,
            created_at=row.created_at,
            completed_at=row.completed_at,
        )

    def _to_root_cause(self, row: RootCauseModel) -> RootCauseHypothesis:
        return RootCauseHypothesis(
            category=row.category,
            title=row.title,
            reasoning=row.reasoning,
            confidence=ConfidenceScore(row.confidence),
            evidence=tuple(Evidence(**item) for item in row.evidence or []),
            supporting_logs=tuple(row.supporting_logs or []),
            supporting_metrics=tuple(row.supporting_metrics or []),
        )

    def _to_recommendation(self, row: RecommendationModel) -> Recommendation:
        return Recommendation(
            action=RemediationAction(row.action),
            title=row.title,
            justification=row.justification,
            priority=row.priority,
            risk=row.risk,
            confidence=ConfidenceScore(row.confidence),
            requires_approval=row.requires_approval,
        )

    def _to_report(self, row: ReportModel) -> Report:
        return Report(
            id=row.id,
            format=row.format,
            title=row.title,
            content=row.content,
            created_at=row.created_at,
        )

    async def _replace_children(self, row: InvestigationModel, state: dict) -> None:
        inv_id = row.id
        for model in (RootCauseModel, RecommendationModel, ReportModel, AgentRunModel):
            await self._session.execute(
                delete(model).where(model.investigation_id == inv_id)
            )

        for cand in state.get("root_cause_candidates", []):
            self._session.add(
                RootCauseModel(
                    investigation_id=inv_id,
                    category=RootCauseCategory(cand["category"]),
                    title=cand["title"],
                    reasoning=cand["reasoning"],
                    confidence=float(cand["confidence"]),
                    evidence=cand.get("evidence", []),
                    supporting_logs=cand.get("supporting_logs", []),
                    supporting_metrics=cand.get("supporting_metrics", []),
                )
            )

        for rec in state.get("recommendations", []):
            self._session.add(
                RecommendationModel(
                    investigation_id=inv_id,
                    action=rec["action"],
                    title=rec["title"],
                    justification=rec["justification"],
                    priority=RecommendationPriority(rec["priority"]),
                    risk=RiskLevel(rec["risk"]),
                    confidence=float(rec["confidence"]),
                    requires_approval=bool(rec.get("requires_approval", True)),
                )
            )

        for report in state.get("reports", []):
            self._session.add(
                ReportModel(
                    investigation_id=inv_id,
                    format=ReportFormat(report.get("format", "markdown")),
                    title=report["title"],
                    content=report["content"],
                )
            )

        errors_by_agent = {e.get("agent"): e for e in state.get("errors", [])}
        for agent_value, score in state.get("confidence_scores", {}).items():
            try:
                agent = AgentName(agent_value)
            except ValueError:
                continue
            err = errors_by_agent.get(agent_value)
            self._session.add(
                AgentRunModel(
                    investigation_id=inv_id,
                    agent=agent,
                    status="failed" if err else "success",
                    retry_count=int(err.get("attempts", 0)) if err else 0,
                    confidence=float(score),
                    error=err.get("error") if err else None,
                )
            )
