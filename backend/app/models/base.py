"""SQLAlchemy declarative base and shared column mixins (2.0 typed style)."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum as SAEnum, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


def sa_enum(enum_cls: type[enum.Enum], name: str) -> SAEnum:
    """Build a SQLAlchemy Enum that persists the member VALUE, not its name.

    Our string enums use lowercase values (e.g. ``bad_deployment``); the Alembic enum types
    are defined with those values. ``values_callable`` makes the ORM agree, keeping SQLite
    tests and Postgres deployments consistent.
    """
    return SAEnum(enum_cls, name=name, values_callable=lambda e: [m.value for m in e])


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
