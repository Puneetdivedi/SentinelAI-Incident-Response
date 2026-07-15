import { Link } from "react-router-dom";
import { useIncidents, useInvestigations } from "@/hooks/queries";
import { PageHeader, SeverityBadge, Spinner, StatusBadge } from "@/components/ui";

function Stat({ label, value, tone = "text-slate-900" }: { label: string; value: number | string; tone?: string }) {
  return (
    <div className="card">
      <div className="text-sm text-slate-500">{label}</div>
      <div className={`mt-2 text-3xl font-semibold ${tone}`}>{value}</div>
    </div>
  );
}

export function Dashboard() {
  const incidents = useIncidents();
  const investigations = useInvestigations();

  if (incidents.isLoading || investigations.isLoading)
    return <Spinner label="Loading dashboard…" />;

  const openIncidents = (incidents.data ?? []).filter((i) => i.status !== "closed" && i.status !== "resolved");
  const awaiting = (investigations.data ?? []).filter((i) => i.status === "awaiting_approval");

  return (
    <div>
      <PageHeader title="Dashboard" subtitle="Live operational overview" />
      <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-4">
        <Stat label="Total incidents" value={incidents.data?.length ?? 0} />
        <Stat label="Active" value={openIncidents.length} tone="text-amber-600" />
        <Stat label="Investigations" value={investigations.data?.length ?? 0} />
        <Stat label="Awaiting approval" value={awaiting.length} tone="text-purple-600" />
      </div>

      <div className="card">
        <h2 className="mb-4 text-lg font-semibold text-slate-900">Recent incidents</h2>
        {openIncidents.length === 0 ? (
          <p className="text-sm text-slate-400">No active incidents.</p>
        ) : (
          <ul className="divide-y divide-slate-100">
            {openIncidents.slice(0, 6).map((incident) => (
              <li key={incident.id}>
                <Link to={`/incidents/${incident.id}`} className="flex items-center justify-between py-3 hover:opacity-80">
                  <div>
                    <div className="font-medium text-slate-800">{incident.title}</div>
                    <div className="text-xs text-slate-400">{incident.affected_service ?? "—"}</div>
                  </div>
                  <div className="flex items-center gap-2">
                    <SeverityBadge severity={incident.severity} />
                    <StatusBadge status={incident.status} />
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
