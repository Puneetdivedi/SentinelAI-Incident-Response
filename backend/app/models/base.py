"""SQLAlchemy declarative base and shared column mixins (2.0 typed style)."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


def _uuid_str() -> str:
    return str(uuid.uuid4())


class UUIDPrimaryKeyMixin:
    """String UUID primary key, portable across Postgres and SQLite (tests)."""

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=_uuid_str
    )


class TimestampMixin:
    """Server-managed created/updated timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
