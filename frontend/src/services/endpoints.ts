import { api } from "./api";
import type {
  Incident,
  IncidentCreate,
  InvestigationDetail,
  InvestigationSummary,
  TokenPair,
  User,
} from "@/types";

export const authApi = {
  login: (email: string, password: string) =>
    api.post<TokenPair>("/auth/login", { email, password }).then((r) => r.data),
  me: () => api.get<User>("/auth/me").then((r) => r.data),
};

export const incidentsApi = {
  list: () => api.get<Incident[]>("/incidents").then((r) => r.data),
  get: (id: string) => api.get<Incident>(`/incidents/${id}`).then((r) => r.data),
  create: (payload: IncidentCreate) =>
    api.post<Incident>("/incidents", payload).then((r) => r.data),
  investigate: (id: string) =>
    api
      .post<InvestigationDetail>(`/incidents/${id}/investigate`, {})
      .then((r) => r.data),
};

export const investigationsApi = {
  list: (incidentId?: string) =>
    api
      .get<InvestigationSummary[]>("/investigations", {
        params: incidentId ? { incident_id: incidentId } : undefined,
      })
      .then((r) => r.data),
  get: (id: string) =>
    api.get<InvestigationDetail>(`/investigations/${id}`).then((r) => r.data),
  approve: (id: string, approved: boolean, note?: string) =>
    api
      .post<InvestigationDetail>(`/investigations/${id}/approve`, { approved, note })
      .then((r) => r.data),
};
