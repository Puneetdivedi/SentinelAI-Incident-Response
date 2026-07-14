"""Domain enumerations.

Framework-free. These enums express the ubiquitous language of the incident-response
domain and are shared across ORM models, Pydantic schemas, and the agent graph.
"""

from __future__ import annotations

from enum import Enum


class UserRole(str, Enum):
    """Role-based access control tiers."""

    ADMIN = "admin"
    SRE = "sre"
    VIEWER = "viewer"


class IncidentSeverity(str, Enum):
    """Severity ranking, aligned with common SEV conventions (SEV1 = worst)."""

    SEV1 = "sev1"
    SEV2 = "sev2"
    SEV3 = "sev3"
    SEV4 = "sev4"


class IncidentStatus(str, Enum):
    """Lifecycle of an incident."""

    OPEN = "open"
    INVESTIGATING = "investigating"
    MITIGATED = "mitigated"
    RESOLVED = "resolved"
    CLOSED = "closed"


class InvestigationStatus(str, Enum):
    """Lifecycle of an autonomous investigation run through the agent graph."""

    PENDING = "pending"
    RUNNING = "running"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentName(str, Enum):
    """Canonical identifiers for every agent in the supervisor graph."""

    SUPERVISOR = "supervisor"
    PLANNER = "planner"
    ALERT_ANALYSIS = "alert_analysis"
    LOG_ANALYSIS = "log_analysis"
    METRICS_ANALYSIS = "metrics_analysis"
    DEPLOYMENT_ANALYSIS = "deployment_analysis"
    DEPENDENCY_ANALYSIS = "dependency_analysis"
    HISTORICAL_INCIDENT = "historical_incident"
    CORRELATION = "correlation"
    ROOT_CAUSE = "root_cause"
    RECOMMENDATION = "recommendation"
    REFLECTION = "reflection"
    INCIDENT_REPORT = "incident_report"
    NOTIFICATION = "notification"


class RootCauseCategory(str, Enum):
    """Taxonomy of probable root causes the Root Cause agent can hypothesize."""

    MEMORY_LEAK = "memory_leak"
    DATABASE_LOCK = "database_lock"
    CONNECTION_POOL_EXHAUSTION = "connection_pool_exhaustion"
    REDIS_TIMEOUT = "redis_timeout"
    BAD_DEPLOYMENT = "bad_deployment"
    CONFIGURATION_ERROR = "configuration_error"
    DNS_FAILURE = "dns_failure"
    CERTIFICATE_EXPIRATION = "certificate_expiration"
    DEPENDENCY_FAILURE = "dependency_failure"
    EXTERNAL_API_FAILURE = "external_api_failure"
    UNKNOWN = "unknown"


class RecommendationPriority(str, Enum):
    """How urgently a remediation should be executed."""

    P0 = "p0"
    P1 = "p1"
    P2 = "p2"
    P3 = "p3"


class RiskLevel(str, Enum):
    """Blast-radius / risk of applying a remediation."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RemediationAction(str, Enum):
    """Canonical remediation actions the Recommendation agent can propose."""

    ROLLBACK_DEPLOYMENT = "rollback_deployment"
    RESTART_SERVICE = "restart_service"
    SCALE_PODS = "scale_pods"
    INCREASE_CONNECTION_POOL = "increase_connection_pool"
    FLUSH_CACHE = "flush_cache"
    RESTART_DATABASE = "restart_database"
    ROTATE_CERTIFICATES = "rotate_certificates"
    INVESTIGATE_SQL_QUERIES = "investigate_sql_queries"
    OPEN_INCIDENT = "open_incident"
    ESCALATE_TO_TEAM = "escalate_to_team"


class ApprovalStatus(str, Enum):
    """Human-in-the-loop approval gate outcomes."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ReportFormat(str, Enum):
    """Supported export formats for the incident report."""

    MARKDOWN = "markdown"
    PDF = "pdf"
    DOCX = "docx"


class LogSource(str, Enum):
    """Origin of a log stream (mock-first, real providers later)."""

    KUBERNETES = "kubernetes"
    NGINX = "nginx"
    FASTAPI = "fastapi"
    POSTGRESQL = "postgresql"


class MetricType(str, Enum):
    """Time-series metric families."""

    CPU = "cpu"
    MEMORY = "memory"
    LATENCY = "latency"
    ERROR_RATE = "error_rate"
    DB_CONNECTIONS = "db_connections"
