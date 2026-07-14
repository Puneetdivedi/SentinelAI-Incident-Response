"""Initial schema: users, incidents, investigations and children, reports, audit logs.

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-14
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# ── Enum type definitions ────────────────────────────────────────────────────
user_role = sa.Enum("admin", "sre", "viewer", name="user_role")
incident_severity = sa.Enum("sev1", "sev2", "sev3", "sev4", name="incident_severity")
incident_status = sa.Enum(
    "open", "investigating", "mitigated", "resolved", "closed", name="incident_status"
)
investigation_status = sa.Enum(
    "pending",
    "running",
    "awaiting_approval",
    "approved",
    "rejected",
    "completed",
    "failed",
    name="investigation_status",
)
approval_status = sa.Enum("pending", "approved", "rejected", name="approval_status")
agent_name = sa.Enum(
    "supervisor",
    "planner",
    "alert_analysis",
    "log_analysis",
    "metrics_analysis",
    "deployment_analysis",
    "dependency_analysis",
    "historical_incident",
    "correlation",
    "root_cause",
    "recommendation",
    "reflection",
    "incident_report",
    "notification",
    name="agent_name",
)
root_cause_category = sa.Enum(
    "memory_leak",
    "database_lock",
    "connection_pool_exhaustion",
    "redis_timeout",
    "bad_deployment",
    "configuration_error",
    "dns_failure",
    "certificate_expiration",
    "dependency_failure",
    "external_api_failure",
    "unknown",
    name="root_cause_category",
)
recommendation_priority = sa.Enum("p0", "p1", "p2", "p3", name="recommendation_priority")
risk_level = sa.Enum("low", "medium", "high", name="risk_level")
report_format = sa.Enum("markdown", "pdf", "docx", name="report_format")


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    ]


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        *_timestamps(),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "incidents",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("severity", incident_severity, nullable=False),
        sa.Column("status", incident_status, nullable=False),
        sa.Column("affected_service", sa.String(length=255), nullable=True),
        sa.Column(
            "created_by",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamps(),
    )
    op.create_index("ix_incidents_status", "incidents", ["status"])

    op.create_table(
        "investigations",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "incident_id",
            sa.String(length=36),
            sa.ForeignKey("incidents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", investigation_status, nullable=False),
        sa.Column("approval_status", approval_status, nullable=False),
        sa.Column("logs", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("alerts", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("metrics", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("deployments", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("dependencies", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("timeline", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("execution_plan", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column(
            "historical_match_ids", sa.JSON(), nullable=False, server_default="[]"
        ),
        sa.Column("confidence_scores", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("errors", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("langfuse_trace_id", sa.String(length=255), nullable=True),
        sa.Column("langfuse_session_id", sa.String(length=255), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "approved_by",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        *_timestamps(),
    )
    op.create_index(
        "ix_investigations_incident_id", "investigations", ["incident_id"]
    )
    op.create_index("ix_investigations_status", "investigations", ["status"])

    op.create_table(
        "agent_runs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "investigation_id",
            sa.String(length=36),
            sa.ForeignKey("investigations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("agent", agent_name, nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("output", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("latency_ms", sa.Float(), nullable=True),
        sa.Column("langfuse_run_id", sa.String(length=255), nullable=True),
        *_timestamps(),
    )
    op.create_index(
        "ix_agent_runs_investigation_id", "agent_runs", ["investigation_id"]
    )

    op.create_table(
        "root_causes",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "investigation_id",
            sa.String(length=36),
            sa.ForeignKey("investigations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("category", root_cause_category, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("reasoning", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("supporting_logs", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column(
            "supporting_metrics", sa.JSON(), nullable=False, server_default="[]"
        ),
        *_timestamps(),
    )
    op.create_index(
        "ix_root_causes_investigation_id", "root_causes", ["investigation_id"]
    )

    op.create_table(
        "recommendations",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "investigation_id",
            sa.String(length=36),
            sa.ForeignKey("investigations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("justification", sa.Text(), nullable=False),
        sa.Column("priority", recommendation_priority, nullable=False),
        sa.Column("risk", risk_level, nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column(
            "requires_approval", sa.Boolean(), nullable=False, server_default=sa.true()
        ),
        *_timestamps(),
    )
    op.create_index(
        "ix_recommendations_investigation_id", "recommendations", ["investigation_id"]
    )

    op.create_table(
        "reports",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "investigation_id",
            sa.String(length=36),
            sa.ForeignKey("investigations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("format", report_format, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("file_path", sa.String(length=512), nullable=True),
        *_timestamps(),
    )
    op.create_index("ix_reports_investigation_id", "reports", ["investigation_id"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "actor_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("action", sa.String(length=128), nullable=False),
        sa.Column("resource_type", sa.String(length=64), nullable=False),
        sa.Column("resource_id", sa.String(length=36), nullable=True),
        sa.Column("detail", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        *_timestamps(),
    )
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("reports")
    op.drop_table("recommendations")
    op.drop_table("root_causes")
    op.drop_table("agent_runs")
    op.drop_table("investigations")
    op.drop_table("incidents")
    op.drop_table("users")

    for enum in (
        report_format,
        risk_level,
        recommendation_priority,
        root_cause_category,
        agent_name,
        approval_status,
        investigation_status,
        incident_status,
        incident_severity,
        user_role,
    ):
        enum.drop(op.get_bind(), checkfirst=True)
