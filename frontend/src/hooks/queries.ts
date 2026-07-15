import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { incidentsApi, investigationsApi } from "@/services/endpoints";
import type { IncidentCreate } from "@/types";

export function useIncidents() {
  return useQuery({ queryKey: ["incidents"], queryFn: incidentsApi.list });
}

export function useIncident(id: string) {
  return useQuery({
    queryKey: ["incident", id],
    queryFn: () => incidentsApi.get(id),
    enabled: Boolean(id),
  });
}

export function useCreateIncident() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: IncidentCreate) => incidentsApi.create(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["incidents"] }),
  });
}

export function useInvestigate() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (incidentId: string) => incidentsApi.investigate(incidentId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["investigations"] });
      qc.invalidateQueries({ queryKey: ["incidents"] });
    },
  });
}

export function useInvestigations(incidentId?: string) {
  return useQuery({
    queryKey: ["investigations", incidentId ?? "all"],
    queryFn: () => investigationsApi.list(incidentId),
  });
}

export function useInvestigation(id: string) {
  return useQuery({
    queryKey: ["investigation", id],
    queryFn: () => investigationsApi.get(id),
    enabled: Boolean(id),
  });
}

export function useApprove(id: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ approved, note }: { approved: boolean; note?: string }) =>
      investigationsApi.approve(id, approved, note),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["investigation", id] });
      qc.invalidateQueries({ queryKey: ["investigations"] });
    },
  });
}
