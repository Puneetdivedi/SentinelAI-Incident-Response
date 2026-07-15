import { Navigate, Route, Routes } from "react-router-dom";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { DashboardLayout } from "@/layouts/DashboardLayout";
import { Dashboard } from "@/pages/Dashboard";
import { Historical } from "@/pages/Historical";
import { IncidentDetail } from "@/pages/IncidentDetail";
import { Incidents } from "@/pages/Incidents";
import { InvestigationDetail } from "@/pages/InvestigationDetail";
import { Investigations } from "@/pages/Investigations";
import { Login } from "@/pages/Login";
import { Settings } from "@/pages/Settings";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<Dashboard />} />
        <Route path="/incidents" element={<Incidents />} />
        <Route path="/incidents/:id" element={<IncidentDetail />} />
        <Route path="/investigations" element={<Investigations />} />
        <Route path="/investigations/:id" element={<InvestigationDetail />} />
        <Route path="/historical" element={<Historical />} />
        <Route path="/settings" element={<Settings />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
