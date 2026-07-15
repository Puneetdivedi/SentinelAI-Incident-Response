import { useNavigate } from "react-router-dom";
import { useInvestigations } from "@/hooks/queries";
import { EmptyState, PageHeader, Spinner, StatusBadge } from "@/components/ui";

export function Investigations() {
  const { data, isLoading } = useInvestigations();
  const navigate = useNavigate();

  if (isLoading) return <Spinner label="Loading investigations…" />;
  if (!data || data.length === 0) return <EmptyState message="No investigations yet." />;

  return (
    <div>
      <PageHeader title="Investigations" subtitle="Autonomous investigation runs" />
      <div className="card overflow-hidden p-0">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-left text-xs uppercase text-slate-400">
            <tr>
              <th className="px-5 py-3">ID</th>
              <th className="px-5 py-3">Incident</th>
              <th className="px-5 py-3">Status</th>
              <th className="px-5 py-3">Approval</th>
              <th className="px-5 py-3">Created</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {data.map((inv) => (
              <tr
                key={inv.id}
                className="cursor-pointer hover:bg-slate-50"
                onClick={() => navigate(`/investigations/${inv.id}`)}
              >
                <td className="px-5 py-3 font-mono text-xs text-brand-700">{inv.id.slice(0, 8)}</td>
                <td className="px-5 py-3 font-mono text-xs text-slate-500">{inv.incident_id.slice(0, 8)}</td>
                <td className="px-5 py-3"><StatusBadge status={inv.status} /></td>
                <td className="px-5 py-3"><StatusBadge status={inv.approval_status} /></td>
                <td className="px-5 py-3 text-slate-500">{new Date(inv.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
