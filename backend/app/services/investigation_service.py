"""Investigation orchestration service.

Coordinates the agent graph and persistence: creates incidents/investigations, runs the
graph to the human-approval interrupt, snapshots state to the DB, and resumes on decision.
"""

from __future__ import annotations

from app.config.logging import get_logger
from app.domain.enums import (
    ApprovalStatus,
    IncidentSeverity,
    IncidentStatus,
    InvestigationStatus,
)
from app.domain.exceptions import EntityNotFoundError, InvestigationError, ValidationError
from app.graphs.runner import InvestigationGraphRunner
from app.models.incident import IncidentModel
from app.models.investigation import InvestigationModel
from app.repositories.interfaces import (
    AuditLogRepository,
    IncidentRepository,
    InvestigationRepository,
)
from app.schemas.incident import InvestigationDetail, ReportRead
from app.services.audit_service import AuditService
from app.state.investigation_state import build_initial_state

logger = get_logger(__name__)


class InvestigationService:
    def __init__(
        self,
        *,
        incidents: IncidentRepository,
        investigations: InvestigationRepository,
        runner: InvestigationGraphRunner,
        audit_repository: AuditLogRepository,
    ) -> None:
        self._incidents = incidents
        self._investigations = investigations
        self._runner = runner
        self._audit = AuditService(audit_repository)

    # ── Incidents ────────────────────────────────────────────
    async def create_incident(
        self,
        *,
        title: str,
        description: str,
        severity: IncidentSeverity,
        affected_service: str | None,
        actor_id: str | None,
    ) -> IncidentModel:
        incident = await self._incidents.create(
            title=title,
            description=description,
            severity=severity,
            affected_service=affected_service,
            created_by=actor_id,
        )
        await self._audit.record(
            action="incident.create", resource_type="incident",
            actor_id=actor_id, resource_id=incident.id,
        )
        return incident

    async def list_incidents(self, *, limit: int = 50, offset: int = 0) -> list[IncidentModel]:
        return await self._incidents.list(limit=limit, offset=offset)

    async def get_incident(self, incident_id: str) -> IncidentModel:
        incident = await self._incidents.get(incident_id)
        if incident is None:
            raise EntityNotFoundError(f"Incident '{incident_id}' not found.")
        return incident

    # ── Investigations ───────────────────────────────────────
    async def start_investigation(
        self, *, incident_id: str, actor_id: str | None
    ) -> InvestigationDetail:
        incident = await self.get_incident(incident_id)
        investigation = await self._investigations.create(incident_id=incident_id)
        await self._incidents.set_status(incident_id, IncidentStatus.INVESTIGATING)

        initial = build_initial_state(
            incident_id=incident.id,
            incident_description=incident.description,
            affected_service=incident.affected_service,
            langfuse_session_id=investigation.id,
        )
        state = await self._runner.start(initial, thread_id=investigation.id)

        saved = await self._investigations.save_state(
            investigation.id,
            state,
            status=InvestigationStatus.AWAITING_APPROVAL,
            approval_status=ApprovalStatus.PENDING,
        )
        await self._audit.record(
            action="investigation.start", resource_type="investigation",
            actor_id=actor_id, resource_id=investigation.id,
        )
        logger.info("investigation.started", extra={"investigation_id": investigation.id})
        return self._to_detail(saved)

    async def decide(
        self, *, investigation_id: str, approved: bool, actor_id: str | None, note: str | None = None
    ) -> InvestigationDetail:
        investigation = await self._investigations.get(investigation_id)
        if investigation is None:
            raise EntityNotFoundError(f"Investigation '{investigation_id}' not found.")
        if investigation.status != InvestigationStatus.AWAITING_APPROVAL:
            raise ValidationError("This investigation is not awaiting approval.")
        if not await self._runner.is_awaiting_approval(thread_id=investigation_id):
            raise InvestigationError(
                "Approval context is no longer available (process restart). "
                "Re-run the investigation."
            )

        final = await self._runner.resume(thread_id=investigation_id, approved=approved)
        status = InvestigationStatus.COMPLETED if approved else InvestigationStatus.REJECTED
        approval = ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED

        saved = await self._investigations.save_state(
            investigation_id, final, status=status, approval_status=approval,
            completed=True, approved_by=actor_id,
        )
        await self._audit.record(
            action="investigation.approve" if approved else "investigation.reject",
            resource_type="investigation", actor_id=actor_id,
            resource_id=investigation_id, detail=note,
        )
        return self._to_detail(saved)

    async def get_investigation(self, investigation_id: str) -> InvestigationDetail:
        row = await self._investigations.get(investigation_id)
        if row is None:
            raise EntityNotFoundError(f"Investigation '{investigation_id}' not found.")
        return self._to_detail(row)

    async def list_investigations(
        self, *, incident_id: str | None = None, limit: int = 50, offset: int = 0
    ) -> list[InvestigationModel]:
        return await self._investigations.list(
            incident_id=incident_id, limit=limit, offset=offset
        )

    # ── Mapping ──────────────────────────────────────────────
    @staticmethod
    def _to_detail(row: InvestigationModel) -> InvestigationDetail:
        return InvestigationDetail(
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
            root_cause_candidates=[
                {
                    "category": rc.category.value,
                    "title": rc.title,
                    "reasoning": rc.reasoning,
                    "confidence": rc.confidence,
                    "evidence": rc.evidence,
                    "supporting_logs": rc.supporting_logs,
                    "supporting_metrics": rc.supporting_metrics,
                }
                for rc in row.root_causes
            ],
            recommendations=[
                {
                    "action": r.action,
                    "title": r.title,
                    "justification": r.justification,
                    "priority": r.priority.value,
                    "risk": r.risk.value,
                    "confidence": r.confidence,
                    "requires_approval": r.requires_approval,
                }
                for r in row.recommendations
            ],
            reports=[ReportRead.model_validate(rp) for rp in row.reports],
            confidence_scores=row.confidence_scores or {},
            errors=row.errors or [],
            langfuse_trace_id=row.langfuse_trace_id,
            langfuse_session_id=row.langfuse_session_id,
            created_at=row.created_at,
            completed_at=row.completed_at,
        )
