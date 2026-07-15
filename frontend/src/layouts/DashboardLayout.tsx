import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { Badge } from "@/components/ui";

const NAV = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/incidents", label: "Incidents" },
  { to: "/investigations", label: "Investigations" },
  { to: "/historical", label: "Historical" },
  { to: "/settings", label: "Settings" },
];

export function DashboardLayout() {
  const { user, logout } = useAuth();

  return (
    <div className="flex h-full">
      <aside className="flex w-60 flex-col border-r border-slate-200 bg-white">
        <div className="flex items-center gap-2 px-5 py-5">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-600 font-bold text-white">
            S
          </div>
          <div>
            <div className="text-sm font-semibold text-slate-900">SentinelAI</div>
            <div className="text-xs text-slate-400">Incident Response</div>
          </div>
        </div>
        <nav className="flex-1 space-y-1 px-3">
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `block rounded-lg px-3 py-2 text-sm font-medium ${
                  isActive
                    ? "bg-brand-50 text-brand-700"
                    : "text-slate-600 hover:bg-slate-50"
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="border-t border-slate-200 p-4">
          <div className="mb-2 text-sm font-medium text-slate-700">{user?.full_name}</div>
          <div className="mb-3">{user && <Badge tone="blue">{user.role}</Badge>}</div>
          <button className="btn-ghost w-full" onClick={logout}>
            Sign out
          </button>
        </div>
      </aside>
      <main className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-6xl px-8 py-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
