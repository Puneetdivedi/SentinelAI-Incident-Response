import { useMemo } from "react";
import { Link } from "react-router-dom";
import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useIncidents, useInvestigations } from "@/hooks/queries";
import { PageHeader, SeverityBadge, Spinner, StatusBadge } from "@/components/ui";

const SEVERITY_COLORS: Record<string, string> = {
  sev1: "#ef4444",
  sev2: "#f59e0b",
  sev3: "#2563eb",
  sev4: "#64748b",
};

const STATUS_COLORS: Record<string, string> = {
  pending: "#64748b",
  running: "#2563eb",
  awaiting_approval: "#8b5cf6",
  approved: "#16a34a",
  rejected: "#dc2626",
  completed: "#16a34a",
  failed: "#ef4444",
};

function StatCard({ label, value, tone = "text-slate-900" }: { label: string; value: number | string; tone?: string }) {
  return (
    <div className="card border-slate-200 bg-slate-50 p-6">
      <div className="text-sm uppercase tracking-[0.12em] text-slate-500">{label}</div>
      <div className={`mt-4 text-4xl font-semibold ${tone}`}>{value}</div>
    </div>
  );
}

export function Dashboard() {
  const incidents = useIncidents();
  const investigations = useInvestigations();

  if (incidents.isLoading || investigations.isLoading) return <Spinner label="Loading dashboard…" />;

  const incidentList = incidents.data ?? [];
  const investigationList = investigations.data ?? [];
  const activeIncidents = incidentList.filter((incident) => incident.status !== "closed" && incident.status !== "resolved");
  const awaitingApproval = investigationList.filter((investigation) => investigation.status === "awaiting_approval");

  const severityData = useMemo(
    () =>
      ["sev1", "sev2", "sev3", "sev4"].map((severity) => ({
        severity: severity.toUpperCase(),
        count: incidentList.filter((incident) => incident.severity === severity).length,
      })),
    [incidentList],
  );

  const investigationStatusData = useMemo(
    () =>
      Object.entries(
        investigationList.reduce<Record<string, number>>((acc, investigation) => {
          acc[investigation.status] = (acc[investigation.status] ?? 0) + 1;
          return acc;
        }, {}),
      ).map(([status, count]) => ({ name: status.replace(/_/g, " "), value: count, status })),
    [investigationList],
  );

  const recentIncidents = activeIncidents
    .slice()
    .sort((a, b) => (a.created_at < b.created_at ? 1 : -1))
    .slice(0, 6);

  return (
    <div className="space-y-8">
      <PageHeader
        title="Operations dashboard"
        subtitle="A real-time view of incident and investigation health."
        action={
          <Link to="/incidents" className="btn-primary inline-flex items-center px-5 py-2.5">
            View incidents
          </Link>
        }
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Total incidents" value={incidentList.length} />
        <StatCard label="Active incidents" value={activeIncidents.length} tone="text-amber-600" />
        <StatCard label="Investigations" value={investigationList.length} tone="text-slate-900" />
        <StatCard label="Awaiting approval" value={awaitingApproval.length} tone="text-purple-600" />
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        <section className="card xl:col-span-2">
          <div className="mb-5 flex items-start justify-between gap-4">
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Severity distribution</h2>
              <p className="mt-1 text-sm text-slate-500">How active incidents are spread across severity levels.</p>
            </div>
            <div className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-slate-600">
              {incidentList.length} incidents
            </div>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={severityData} margin={{ top: 10, right: 16, bottom: 10, left: 0 }}>
                <CartesianGrid stroke="#e2e8f0" strokeDasharray="3 3" horizontal={false} />
                <XAxis dataKey="severity" stroke="#64748b" tickLine={false} axisLine={false} />
                <YAxis stroke="#64748b" tickLine={false} axisLine={false} />
                <Tooltip formatter={(value: number) => [`${value}`, "Count"]} />
                <Bar dataKey="count" radius={[12, 12, 0, 0]} fill="#2563eb">
                  {severityData.map((entry) => (
                    <Cell key={entry.severity} fill={SEVERITY_COLORS[entry.severity.toLowerCase()] ?? "#2563eb"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="card">
          <div className="mb-5">
            <h2 className="text-lg font-semibold text-slate-900">Investigation status</h2>
            <p className="mt-1 text-sm text-slate-500">Current workflow progress across investigations.</p>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={investigationStatusData} dataKey="value" nameKey="name" innerRadius={50} outerRadius={90} paddingAngle={4}>
                  {investigationStatusData.map((entry) => (
                    <Cell key={entry.name} fill={STATUS_COLORS[entry.status] ?? "#94a3b8"} />
                  ))}
                </Pie>
                <Tooltip formatter={(value: number) => [`${value}`, "Investigations"]} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 space-y-2">
            {investigationStatusData.map((entry) => (
              <div key={entry.name} className="flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3 text-sm">
                <div className="flex items-center gap-3">
                  <span className="inline-block h-3.5 w-3.5 rounded-full" style={{ background: STATUS_COLORS[entry.status] }} />
                  <span className="font-medium text-slate-700">{entry.name}</span>
                </div>
                <span className="font-semibold text-slate-900">{entry.value}</span>
              </div>
            ))}
          </div>
        </section>
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <section className="card">
          <div className="mb-5 flex items-start justify-between gap-4">
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Recent active incidents</h2>
              <p className="mt-1 text-sm text-slate-500">Quick access to the most recently created active incident reports.</p>
            </div>
            <Link to="/incidents" className="text-sm font-medium text-brand-600 hover:text-brand-700">
              View all
            </Link>
          </div>
          {recentIncidents.length === 0 ? (
            <p className="text-sm text-slate-400">No active incidents at this time.</p>
          ) : (
            <div className="divide-y divide-slate-200">
              {recentIncidents.map((incident) => (
                <Link
                  key={incident.id}
                  to={`/incidents/${incident.id}`}
                  className="flex flex-col gap-3 border-b border-slate-100 px-0 py-4 last:border-b-0 hover:bg-slate-50"
                >
                  <div className="flex items-center justify-between gap-4">
                    <div>
                      <p className="font-semibold text-slate-900">{incident.title}</p>
                      <p className="mt-1 text-sm text-slate-500">{incident.affected_service ?? "Unknown service"}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <SeverityBadge severity={incident.severity} />
                      <StatusBadge status={incident.status} />
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2 text-xs text-slate-500">
                    <span>{new Date(incident.created_at).toLocaleDateString()}</span>
                    <span>Created by {incident.created_by ?? "system"}</span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </section>

        <section className="card">
          <div className="mb-5">
            <h2 className="text-lg font-semibold text-slate-900">Operational summary</h2>
            <p className="mt-1 text-sm text-slate-500">Key performance indicators at a glance.</p>
          </div>
          <div className="grid gap-4">
            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
              <p className="text-sm text-slate-500">Average response time</p>
              <p className="mt-3 text-3xl font-semibold text-slate-900">24m</p>
            </div>
            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
              <p className="text-sm text-slate-500">Escalations this week</p>
              <p className="mt-3 text-3xl font-semibold text-amber-600">3</p>
            </div>
            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
              <p className="text-sm text-slate-500">Resolved incidents</p>
              <p className="mt-3 text-3xl font-semibold text-green-600">{incidentList.filter((incident) => incident.status === "resolved").length}</p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
