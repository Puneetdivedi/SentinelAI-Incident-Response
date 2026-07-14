"""ORM models package.

Importing this package registers every model on ``Base.metadata`` so Alembic autogenerate
and ``create_all`` see the full schema. Import order avoids relationship resolution gaps.
"""

from __future__ import annotations

from app.models.base import Base
from app.models.user import UserModel
from app.models.incident import IncidentModel
from app.models.investigation import (
    AgentRunModel,
    InvestigationModel,
    RecommendationModel,
    RootCauseModel,
)
from app.models.report import ReportModel
from app.models.audit_log import AuditLogModel

__all__ = [
    "Base",
    "UserModel",
    "IncidentModel",
    "InvestigationModel",
    "AgentRunModel",
    "RootCauseModel",
    "RecommendationModel",
    "ReportModel",
    "AuditLogModel",
]
