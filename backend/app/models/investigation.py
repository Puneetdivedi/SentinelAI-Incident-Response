"""Investigation ORM model and its child records."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import (
    AgentName,
    ApprovalStatus,
    InvestigationStatus,
    RecommendationPriority,
    RiskLevel,
    RootCauseCategory,
)
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, sa_enum


class InvestigationModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "investigations"

    incident_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    status: Mapped[InvestigationStatus] = mapped_column(
        sa_enum(InvestigationStatus, "investigation_status"),
        default=InvestigationStatus.PENDING,
        index=True,
        nullable=False,
    )
    approval_status: Mapped[ApprovalStatus] = mapped_column(
        sa_enum(ApprovalStatus, "approval_status"),
        default=ApprovalStatus.PENDING,
        nullable=False,
    )

    # Denormalized evidence snapshots (JSONB in Postgres, JSON in SQLite).
    logs: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    alerts: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    metrics: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    deployments: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    dependencies: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    timeline: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    execution_plan: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    historical_match_ids: Mapped[list] = mapped_column(
        JSON, default=list, nullable=False
    )
    confidence_scores: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    errors: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    # Observability
    langfuse_trace_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    langfuse_session_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    approved_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    incident: Mapped["IncidentModel"] = relationship(
        "IncidentModel", back_populates="investigations"
    )
    agent_runs: Mapped[list["AgentRunModel"]] = relationship(
        "AgentRunModel",
        back_populates="investigation",
        cascade="all, delete-orphan",
    )
    root_causes: Mapped[list["RootCauseModel"]] = relationship(
        "RootCauseModel",
        back_populates="investigation",
        cascade="all, delete-orphan",
    )
    recommendations: Mapped[list["RecommendationModel"]] = relationship(
        "RecommendationModel",
        back_populates="investigation",
        cascade="all, delete-orphan",
    )
    reports: Mapped[list["ReportModel"]] = relationship(
        "ReportModel",
        back_populates="investigation",
        cascade="all, delete-orphan",
    )


class AgentRunModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Per-agent execution record for observability and replay."""

    __tablename__ = "agent_runs"

    investigation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("investigations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    agent: Mapped[AgentName] = mapped_column(
        sa_enum(AgentName, "agent_name"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    retry_count: Mapped[int] = mapped_column(default=0, nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    output: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    langfuse_run_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    investigation: Mapped["InvestigationModel"] = relationship(
        "InvestigationModel", back_populates="agent_runs"
    )


class RootCauseModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A persisted root-cause hypothesis."""

    __tablename__ = "root_causes"

    investigation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("investigations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    category: Mapped[RootCauseCategory] = mapped_column(
        sa_enum(RootCauseCategory, "root_cause_category"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    evidence: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    supporting_logs: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    supporting_metrics: Mapped[list] = mapped_column(
        JSON, default=list, nullable=False
    )

    investigation: Mapped["InvestigationModel"] = relationship(
        "InvestigationModel", back_populates="root_causes"
    )


class RecommendationModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A persisted remediation recommendation."""

    __tablename__ = "recommendations"

    investigation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("investigations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    justification: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[RecommendationPriority] = mapped_column(
        sa_enum(RecommendationPriority, "recommendation_priority"), nullable=False
    )
    risk: Mapped[RiskLevel] = mapped_column(
        sa_enum(RiskLevel, "risk_level"), nullable=False
    )
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    requires_approval: Mapped[bool] = mapped_column(default=True, nullable=False)

    investigation: Mapped["InvestigationModel"] = relationship(
        "InvestigationModel", back_populates="recommendations"
    )
