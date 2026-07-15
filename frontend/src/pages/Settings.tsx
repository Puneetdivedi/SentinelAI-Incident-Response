import { useAuth } from "@/contexts/AuthContext";
import { Badge, PageHeader } from "@/components/ui";

export function Settings() {
  const { user } = useAuth();
  const traceHost = "https://cloud.langfuse.com";

  return (
    <div>
      <PageHeader title="Settings" subtitle="Profile and platform configuration" />

      <div className="card mb-6">
        <h2 className="mb-4 text-lg font-semibold text-slate-900">Profile</h2>
        <dl className="grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
          <div>
            <dt className="text-slate-400">Name</dt>
            <dd className="font-medium text-slate-800">{user?.full_name}</dd>
          </div>
          <div>
            <dt className="text-slate-400">Email</dt>
            <dd className="font-medium text-slate-800">{user?.email}</dd>
          </div>
          <div>
            <dt className="text-slate-400">Role</dt>
            <dd>{user && <Badge tone="blue">{user.role}</Badge>}</dd>
          </div>
        </dl>
      </div>

      <div className="card">
        <h2 className="mb-2 text-lg font-semibold text-slate-900">Observability</h2>
        <p className="text-sm text-slate-500">
          LLM interactions are traced in LangFuse. Open the{" "}
          <a href={traceHost} target="_blank" rel="noreferrer" className="text-brand-700 underline">
            LangFuse dashboard
          </a>{" "}
          to inspect prompts, latency, token usage, and cost per investigation.
        </p>
      </div>
    </div>
  );
}
