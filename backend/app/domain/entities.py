"""Domain entities (aggregates).

Framework-free representations of the core business objects. These are distinct from the
SQLAlchemy ORM models in ``app/models`` (persistence) and the Pydantic DTOs in
``app/schemas`` (transport). Repositories translate between ORM rows and these entities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from app.domain.enums import (
    ApprovalStatus,
    IncidentSeverity,
    IncidentStatus,
    InvestigationStatus,
    UserRole,
)
from app.domain.value_objects import (
    Alert,
    Deployment,
    DependencyStatus,
    LogEntry,
    MetricPoint,
    Recommendation,
    Report,
    RootCauseHypothesis,
    TimelineEvent,
)


@dataclass(slots=True)
class User:
    """A platform user subject to RBAC."""

    id: str
    email: str
    full_name: str
    role: UserRole
    hashed_password: str
    is_active: bool = True
    created_at: datetime | None = None

    def has_role(self, *roles: UserRole) -> bool:
        return self.role in roles

    @property
    def can_approve(self) -> bool:
        """Only Admin and SRE may approve remediation."""
        return self.role in (UserRole.ADMIN, UserRole.SRE)


@dataclass(slots=True)
class Incident:
    """An observed production incident."""

    id: str
    title: str
    description: str
    severity: IncidentSeverity
    status: IncidentStatus = IncidentStatus.OPEN
    affected_service: str | None = None
    created_by: str | None = None
    created_at: datetime | None = None
    resolved_at: datetime | None = None


@dataclass(slots=True)
class Investigation:
    """An autonomous investigation executed by the agent graph for an incident."""

    id: str
    incident_id: str
    status: InvestigationStatus = InvestigationStatus.PENDING
    approval_status: ApprovalStatus = ApprovalStatus.PENDING

    # Collected evidence
    logs: list[LogEntry] = field(default_factory=list)
    alerts: list[Alert] = field(default_factory=list)
    metrics: list[MetricPoint] = field(default_factory=list)
    deployments: list[Deployment] = field(default_factory=list)
    dependencies: list[DependencyStatus] = field(default_factory=list)
    timeline: list[TimelineEvent] = field(default_factory=list)

    # Reasoning outputs
    root_cause_candidates: list[RootCauseHypothesis] = field(default_factory=list)
    recommendations: list[Recommendation] = field(default_factory=list)
    historical_match_ids: list[str] = field(default_factory=list)
    reports: list[Report] = field(default_factory=list)
    confidence_scores: dict[str, float] = field(default_factory=dict)
    errors: list[dict] = field(default_factory=list)

    # Observability
    langfuse_trace_id: str | None = None
    langfuse_session_id: str | None = None

    created_at: datetime | None = None
    completed_at: datetime | None = None

    @property
    def top_root_cause(self) -> RootCauseHypothesis | None:
        if not self.root_cause_candidates:
            return None
        return max(self.root_cause_candidates, key=lambda h: h.confidence.value)


@dataclass(slots=True)
class AuditEntry:
    """An immutable audit-trail record of a security-relevant action."""

    id: str
    actor_id: str | None
    action: str
    resource_type: str
    resource_id: str | None
    detail: str | None = None
    ip_address: str | None = None
    created_at: datetime | None = None
