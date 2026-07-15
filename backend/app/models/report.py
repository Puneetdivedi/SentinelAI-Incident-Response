"""Incident report ORM model."""

from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import ReportFormat
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, sa_enum


class ReportModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "reports"

    investigation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("investigations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    format: Mapped[ReportFormat] = mapped_column(
        sa_enum(ReportFormat, "report_format"),
        default=ReportFormat.MARKDOWN,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    # Markdown source is always stored; binary exports (PDF/DOCX) live at file_path.
    content: Mapped[str] = mapped_column(Text, nullable=False)
    file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)

    investigation: Mapped["InvestigationModel"] = relationship(
        "InvestigationModel", back_populates="reports"
    )
