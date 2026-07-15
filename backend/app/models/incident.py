"""Incident ORM model."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import IncidentSeverity, IncidentStatus
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, sa_enum


class IncidentModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "incidents"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[IncidentSeverity] = mapped_column(
        sa_enum(IncidentSeverity, "incident_severity"),
        default=IncidentSeverity.SEV3,
        nullable=False,
    )
    status: Mapped[IncidentStatus] = mapped_column(
        sa_enum(IncidentStatus, "incident_status"),
        default=IncidentStatus.OPEN,
        index=True,
        nullable=False,
    )
    affected_service: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    investigations: Mapped[list["InvestigationModel"]] = relationship(
        "InvestigationModel",
        back_populates="incident",
        cascade="all, delete-orphan",
    )
