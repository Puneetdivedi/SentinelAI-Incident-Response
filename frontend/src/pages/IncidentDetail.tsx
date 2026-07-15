import { useNavigate, useParams } from "react-router-dom";
import { useIncident, useInvestigate, useInvestigations } from "@/hooks/queries";
import { useAuth } from "@/contexts/AuthContext";
import { apiErrorMessage } from "@/services/api";
import { EmptyState, PageHeader, SeverityBadge, Spinner, StatusBadge } from "@/components/ui";
import { useState } from "react";

export function IncidentDetail() {
  const { id = "" } = useParams();
  const navigate = useNavigate();
  const { data: incident, isLoading } = useIncident(id);
  const investigations = useInvestigations(id);
  const investigate = useInvestigate();
  const { user } = useAuth();
  const canManage = user?.role === "admin" || user?.role === "sre";
  const [error, setError] = useState<string | null>(null);

  if (isLoading) return <Spinner label="Loading incident…" />;
  if (!incident) return <EmptyState message="Incident not found." />;

  async function runInvestigation() {
    setError(null);
    try {
      const detail = await investigate.mutateAsync(id);
      navigate(`/investigations/${detail.id}`);
    } catch (err) {
      setError(apiErrorMessage(err));
    }
  }

  return (
    <div>
      <PageHeader
        title={incident.title}
        subtitle={incident.affected_service ?? undefined}
        action={
          canManage && (
            <button className="btn-primary" onClick={runInvestigation} disabled={investigate.isPending}>
              {investigate.isPending ? "Investigating…" : "Investigate"}
            </button>
          )
        }
      />

      <div className="card mb-6">
        <div className="mb-4 flex items-center gap-2">
          <SeverityBadge severity={incident.severity} />
          <StatusBadge status={incident.status} />
        </div>
        <p className="whitespace-pre-wrap text-sm text-slate-700">{incident.description}</p>
        {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
      </div>

      <div className="card">
        <h2 className="mb-4 text-lg font-semibold text-slate-900">Investigations</h2>
        {!investigations.data || investigations.data.length === 0 ? (
          <p className="text-sm text-slate-400">No investigations yet.</p>
        ) : (
          <ul className="divide-y divide-slate-100">
            {investigations.data.map((inv) => (
              <li
                key={inv.id}
                className="flex cursor-pointer items-center justify-between py-3 hover:opacity-80"
                onClick={() => navigate(`/investigations/${inv.id}`)}
              >
                <span className="font-mono text-xs text-slate-500">{inv.id.slice(0, 8)}</span>
                <StatusBadge status={inv.status} />
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
