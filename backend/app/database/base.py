"""Metadata aggregation for Alembic.

Alembic imports ``target_metadata`` from here. Importing ``app.models`` pulls every model
into ``Base.metadata`` so autogenerate produces complete migrations.
"""

from __future__ import annotations

from app.models import Base  # noqa: F401  (re-exported for Alembic)

target_metadata = Base.metadata
