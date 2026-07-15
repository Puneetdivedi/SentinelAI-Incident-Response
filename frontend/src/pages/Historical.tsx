import { useInvestigations } from "@/hooks/queries";
import { EmptyState, PageHeader, Spinner, StatusBadge } from "@/components/ui";

export function Historical() {
  const { data, isLoading } = useInvestigations();
  if (isLoading) return <Spinner label="Loading history…" />;

  const completed = (data ?? []).filter(
    (i) => i.status === "completed" || i.status === "rejected",
  );

  return (
    <div>
      <PageHeader title="Historical Incidents" subtitle="Resolved & rejected investigations" />
      {completed.length === 0 ? (
        <EmptyState message="No completed investigations yet." />
      ) : (
        <div className="space-y-3">
          {completed.map((inv) => (
            <div key={inv.id} className="card flex items-center justify-between">
              <div>
                <div className="font-mono text-xs text-slate-500">{inv.id.slice(0, 8)}</div>
                <div className="text-xs text-slate-400">
                  {inv.completed_at ? new Date(inv.completed_at).toLocaleString() : "—"}
                </div>
              </div>
              <StatusBadge status={inv.approval_status} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
