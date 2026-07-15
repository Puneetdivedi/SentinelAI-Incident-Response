import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { useCreateIncident, useIncidents } from "@/hooks/queries";
import { useAuth } from "@/contexts/AuthContext";
import { apiErrorMessage } from "@/services/api";
import { EmptyState, PageHeader, SeverityBadge, Spinner, StatusBadge } from "@/components/ui";
import type { IncidentSeverity } from "@/types";

export function Incidents() {
  const { data, isLoading } = useIncidents();
  const create = useCreateIncident();
  const { user } = useAuth();
  const canManage = user?.role === "admin" || user?.role === "sre";

  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [severity, setSeverity] = useState<IncidentSeverity>("sev2");
  const [service, setService] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    try {
      await create.mutateAsync({
        title,
        description,
        severity,
        affected_service: service || null,
      });
      setOpen(false);
      setTitle("");
      setDescription("");
      setService("");
    } catch (err) {
      setError(apiErrorMessage(err));
    }
  }

  return (
    <div>
      <PageHeader
        title="Incidents"
        subtitle="Report and track production incidents"
        action={
          canManage && (
            <button className="btn-primary" onClick={() => setOpen((o) => !o)}>
              {open ? "Close" : "New incident"}
            </button>
          )
        }
      />

      {open && (
        <form onSubmit={submit} className="card mb-6 space-y-4">
          <div>
            <label className="label">Title</label>
            <input className="input" value={title} onChange={(e) => setTitle(e.target.value)} required />
          </div>
          <div>
            <label className="label">Description</label>
            <textarea className="input" rows={3} value={description} onChange={(e) => setDescription(e.target.value)} required />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Severity</label>
              <select className="input" value={severity} onChange={(e) => setSeverity(e.target.value as IncidentSeverity)}>
                <option value="sev1">SEV1</option>
                <option value="sev2">SEV2</option>
                <option value="sev3">SEV3</option>
                <option value="sev4">SEV4</option>
              </select>
            </div>
            <div>
              <label className="label">Affected service</label>
              <input className="input" value={service} onChange={(e) => setService(e.target.value)} placeholder="auth-api" />
            </div>
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button type="submit" className="btn-primary" disabled={create.isPending}>
            {create.isPending ? "Creating…" : "Create incident"}
          </button>
        </form>
      )}

      {isLoading ? (
        <Spinner label="Loading incidents…" />
      ) : !data || data.length === 0 ? (
        <EmptyState message="No incidents yet." />
      ) : (
        <div className="card overflow-hidden p-0">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-left text-xs uppercase text-slate-400">
              <tr>
                <th className="px-5 py-3">Title</th>
                <th className="px-5 py-3">Service</th>
                <th className="px-5 py-3">Severity</th>
                <th className="px-5 py-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {data.map((incident) => (
                <tr key={incident.id} className="hover:bg-slate-50">
                  <td className="px-5 py-3">
                    <Link to={`/incidents/${incident.id}`} className="font-medium text-brand-700">
                      {incident.title}
                    </Link>
                  </td>
                  <td className="px-5 py-3 text-slate-500">{incident.affected_service ?? "—"}</td>
                  <td className="px-5 py-3"><SeverityBadge severity={incident.severity} /></td>
                  <td className="px-5 py-3"><StatusBadge status={incident.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
