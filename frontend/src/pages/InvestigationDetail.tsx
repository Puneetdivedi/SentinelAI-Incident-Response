import { lazy, Suspense, useState, type ReactNode } from "react";
import { useParams } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useApprove, useInvestigation } from "@/hooks/queries";
import { useAuth } from "@/contexts/AuthContext";
import { apiErrorMessage } from "@/services/api";
import {
  Badge,
  ConfidenceBar,
  EmptyState,
  PageHeader,
  Spinner,
  StatusBadge,
} from "@/components/ui";
import type { InvestigationDetail as Detail } from "@/types";

// Monaco is heavy; load it only when the raw-state viewer is opened.
const Editor = lazy(() => import("@monaco-editor/react"));

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="card mb-6">
      <h2 className="mb-4 text-lg font-semibold text-slate-900">{title}</h2>
      {children}
    </div>
  );
}

function ApprovalPanel({ investigation }: { investigation: Detail }) {
  const { user } = useAuth();
  const approve = useApprove(investigation.id);
  const [note, setNote] = useState("");
  const [error, setError] = useState<string | null>(null);
  const canApprove = user?.role === "admin" || user?.role === "sre";

  if (investigation.status !== "awaiting_approval") return null;

  async function decide(approved: boolean) {
    setError(null);
    try {
      await approve.mutateAsync({ approved, note: note || undefined });
    } catch (err) {
      setError(apiErrorMessage(err));
    }
  }

  return (
    <Section title="Human Approval Required">
      {!canApprove ? (
        <p className="text-sm text-slate-500">Your role cannot approve remediation.</p>
      ) : (
        <div className="space-y-3">
          <textarea
            className="input"
            rows={2}
            placeholder="Optional note…"
            value={note}
            onChange={(e) => setNote(e.target.value)}
          />
          <div className="flex gap-3">
            <button className="btn-primary" disabled={approve.isPending} onClick={() => decide(true)}>
              Approve remediation
            </button>
            <button className="btn-danger" disabled={approve.isPending} onClick={() => decide(false)}>
              Reject
            </button>
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
        </div>
      )}
    </Section>
  );
}

export function InvestigationDetail() {
  const { id = "" } = useParams();
  const { data, isLoading } = useInvestigation(id);
  const [showRaw, setShowRaw] = useState(false);

  if (isLoading) return <Spinner label="Loading investigation…" />;
  if (!data) return <EmptyState message="Investigation not found." />;

  const metricData = data.metrics.map((m) => ({ name: m.metric, value: m.value }));

  return (
    <div>
      <PageHeader
        title="Investigation"
        subtitle={data.id}
        action={<StatusBadge status={data.status} />}
      />

      <ApprovalPanel investigation={data} />

      {data.execution_plan.length > 0 && (
        <Section title="Execution Plan">
          <ol className="list-decimal space-y-1 pl-5 text-sm text-slate-700">
            {data.execution_plan.map((step, i) => (
              <li key={i}>{step}</li>
            ))}
          </ol>
        </Section>
      )}

      <Section title="Agent Confidence">
        <div className="space-y-2">
          {Object.entries(data.confidence_scores).map(([agent, score]) => (
            <div key={agent} className="flex items-center justify-between">
              <span className="text-sm text-slate-600">{agent.replace(/_/g, " ")}</span>
              <ConfidenceBar value={score} />
            </div>
          ))}
        </div>
      </Section>

      {metricData.length > 0 && (
        <Section title="Metrics">
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={metricData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="value" fill="#2563eb" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Section>
      )}

      <Section title="Timeline">
        {data.timeline.length === 0 ? (
          <p className="text-sm text-slate-400">No timeline events.</p>
        ) : (
          <ol className="relative border-l border-slate-200 pl-6">
            {data.timeline.map((event, i) => (
              <li key={i} className="mb-5">
                <div className="absolute -left-1.5 mt-1 h-3 w-3 rounded-full bg-brand-500" />
                <div className="text-xs text-slate-400">{event.timestamp}</div>
                <div className="font-medium text-slate-800">{event.label}</div>
                <div className="text-sm text-slate-600">{event.detail}</div>
              </li>
            ))}
          </ol>
        )}
      </Section>

      <Section title="Root Cause Candidates">
        {data.root_cause_candidates.length === 0 ? (
          <p className="text-sm text-slate-400">No hypotheses.</p>
        ) : (
          <div className="space-y-4">
            {[...data.root_cause_candidates]
              .sort((a, b) => b.confidence - a.confidence)
              .map((rc, i) => (
                <div key={i} className="rounded-lg border border-slate-200 p-4">
                  <div className="mb-2 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Badge tone="purple">{rc.category.replace(/_/g, " ")}</Badge>
                      <span className="font-medium text-slate-800">{rc.title}</span>
                    </div>
                    <ConfidenceBar value={rc.confidence} />
                  </div>
                  <p className="text-sm text-slate-600">{rc.reasoning}</p>
                  {rc.supporting_logs.length > 0 && (
                    <div className="mt-2 text-xs text-slate-400">
                      Evidence: {rc.supporting_logs.join(" · ")}
                    </div>
                  )}
                </div>
              ))}
          </div>
        )}
      </Section>

      <Section title="Recommendations">
        {data.recommendations.length === 0 ? (
          <p className="text-sm text-slate-400">No recommendations.</p>
        ) : (
          <div className="space-y-3">
            {data.recommendations.map((rec, i) => (
              <div key={i} className="rounded-lg border border-slate-200 p-4">
                <div className="mb-1 flex items-center gap-2">
                  <Badge tone="red">{rec.priority.toUpperCase()}</Badge>
                  <Badge tone="amber">risk: {rec.risk}</Badge>
                  <span className="font-medium text-slate-800">{rec.title}</span>
                </div>
                <p className="text-sm text-slate-600">{rec.justification}</p>
              </div>
            ))}
          </div>
        )}
      </Section>

      {data.reports.length > 0 && (
        <Section title="Report">
          <article className="prose prose-sm max-w-none prose-headings:text-slate-900 prose-p:text-slate-700">
            <ReactMarkdown>{data.reports[0].content}</ReactMarkdown>
          </article>
        </Section>
      )}

      <Section title="Raw State">
        <button className="btn-ghost mb-3" onClick={() => setShowRaw((s) => !s)}>
          {showRaw ? "Hide" : "Show"} raw JSON
        </button>
        {showRaw && (
          <div className="h-96 overflow-hidden rounded-lg border border-slate-200">
            <Suspense fallback={<Spinner label="Loading editor…" />}>
              <Editor
                height="100%"
                defaultLanguage="json"
                value={JSON.stringify(data, null, 2)}
                options={{ readOnly: true, minimap: { enabled: false }, fontSize: 12 }}
              />
            </Suspense>
          </div>
        )}
      </Section>
    </div>
  );
}
