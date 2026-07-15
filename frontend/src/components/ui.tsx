import type { ReactNode } from "react";

const TONES: Record<string, string> = {
  green: "bg-green-100 text-green-700",
  red: "bg-red-100 text-red-700",
  amber: "bg-amber-100 text-amber-700",
  blue: "bg-blue-100 text-blue-700",
  slate: "bg-slate-100 text-slate-600",
  purple: "bg-purple-100 text-purple-700",
};

export function Badge({ tone = "slate", children }: { tone?: keyof typeof TONES | string; children: ReactNode }) {
  return (
    <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold ${TONES[tone] ?? TONES.slate}`}>
      {children}
    </span>
  );
}

const SEVERITY_TONE: Record<string, string> = {
  sev1: "red",
  sev2: "amber",
  sev3: "blue",
  sev4: "slate",
};

export function SeverityBadge({ severity }: { severity: string }) {
  return <Badge tone={SEVERITY_TONE[severity] ?? "slate"}>{severity.toUpperCase()}</Badge>;
}

const STATUS_TONE: Record<string, string> = {
  open: "amber",
  investigating: "blue",
  awaiting_approval: "purple",
  completed: "green",
  approved: "green",
  resolved: "green",
  mitigated: "green",
  rejected: "red",
  failed: "red",
  pending: "slate",
  running: "blue",
  closed: "slate",
};

export function StatusBadge({ status }: { status: string }) {
  return <Badge tone={STATUS_TONE[status] ?? "slate"}>{status.replace(/_/g, " ")}</Badge>;
}

export function ConfidenceBar({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const color = pct >= 75 ? "bg-green-500" : pct >= 50 ? "bg-amber-500" : "bg-red-500";
  return (
    <div className="flex items-center gap-2">
      <div className="h-2 w-28 overflow-hidden rounded-full bg-slate-200">
        <div className={`h-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs font-medium text-slate-500">{pct}%</span>
    </div>
  );
}

export function Spinner({ label }: { label?: string }) {
  return (
    <div className="flex items-center gap-3 text-slate-500">
      <div className="h-5 w-5 animate-spin rounded-full border-2 border-slate-300 border-t-brand-600" />
      {label && <span className="text-sm">{label}</span>}
    </div>
  );
}

export function PageHeader({ title, subtitle, action }: { title: string; subtitle?: string; action?: ReactNode }) {
  return (
    <div className="mb-6 flex items-start justify-between gap-4">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">{title}</h1>
        {subtitle && <p className="mt-1 text-sm text-slate-500">{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}

export function EmptyState({ message }: { message: string }) {
  return (
    <div className="rounded-xl border border-dashed border-slate-300 p-10 text-center text-slate-400">
      {message}
    </div>
  );
}
