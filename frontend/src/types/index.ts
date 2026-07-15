// API types mirroring the backend Pydantic schemas.

export type UserRole = "admin" | "sre" | "viewer";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export type IncidentSeverity = "sev1" | "sev2" | "sev3" | "sev4";
export type IncidentStatus =
  | "open"
  | "investigating"
  | "mitigated"
  | "resolved"
  | "closed";

export interface Incident {
  id: string;
  title: string;
  description: string;
  severity: IncidentSeverity;
  status: IncidentStatus;
  affected_service: string | null;
  created_by: string | null;
  created_at: string;
}

export interface IncidentCreate {
  title: string;
  description: string;
  severity: IncidentSeverity;
  affected_service?: string | null;
}

export type InvestigationStatus =
  | "pending"
  | "running"
  | "awaiting_approval"
  | "approved"
  | "rejected"
  | "completed"
  | "failed";

export type ApprovalStatus = "pending" | "approved" | "rejected";

export interface Report {
  id: string;
  format: string;
  title: string;
  content: string;
  created_at: string;
}

export interface RootCauseCandidate {
  category: string;
  title: string;
  reasoning: string;
  confidence: number;
  evidence: { description: string; source: string; weight: number }[];
  supporting_logs: string[];
  supporting_metrics: string[];
}

export interface Recommendation {
  action: string;
  title: string;
  justification: string;
  priority: string;
  risk: string;
  confidence: number;
  requires_approval: boolean;
}

export interface TimelineEvent {
  timestamp: string;
  label: string;
  detail: string;
  source: string;
}

export interface MetricPoint {
  timestamp: string;
  metric: string;
  value: number;
  unit: string;
  service?: string | null;
}

export interface InvestigationSummary {
  id: string;
  incident_id: string;
  status: InvestigationStatus;
  approval_status: ApprovalStatus;
  created_at: string;
  completed_at: string | null;
}

export interface InvestigationDetail {
  id: string;
  incident_id: string;
  status: InvestigationStatus;
  approval_status: ApprovalStatus;
  execution_plan: string[];
  logs: Record<string, unknown>[];
  alerts: Record<string, unknown>[];
  metrics: MetricPoint[];
  deployments: Record<string, unknown>[];
  dependencies: Record<string, unknown>[];
  timeline: TimelineEvent[];
  historical_match_ids: string[];
  root_cause_candidates: RootCauseCandidate[];
  recommendations: Recommendation[];
  reports: Report[];
  confidence_scores: Record<string, number>;
  errors: Record<string, unknown>[];
  langfuse_trace_id: string | null;
  langfuse_session_id: string | null;
  created_at: string;
  completed_at: string | null;
}
