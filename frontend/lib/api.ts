"use client";

import type { AgentWorkflowTrace, Connection, QueryResult, User, Workspace } from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

export async function apiFetch<T>(path: string, options: RequestInit = {}, token?: string | null): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers
    }
  });
  if (!response.ok) {
    let message = response.statusText;
    try {
      const body = await response.json();
      message = body.detail ?? message;
    } catch {
      // keep response status text
    }
    throw new ApiError(message, response.status);
  }
  return response.json();
}

async function apiBlob(path: string, token?: string | null): Promise<Blob> {
  const response = await fetch(`${API_URL}${path}`, {
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    }
  });
  if (!response.ok) {
    throw new ApiError(response.statusText, response.status);
  }
  return response.blob();
}

export const api = {
  login: (email: string, password: string) =>
    apiFetch<{ access_token: string; user: User }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password })
    }),
  register: (email: string, full_name: string, password: string) =>
    apiFetch<{ access_token: string; user: User }>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, full_name, password })
    }),
  me: (token: string) => apiFetch<User>("/users/me", {}, token),
  workspaces: (token: string) => apiFetch<Workspace[]>("/workspaces", {}, token),
  createWorkspace: (token: string, name: string) =>
    apiFetch<Workspace>("/workspaces", { method: "POST", body: JSON.stringify({ name }) }, token),
  connections: (token: string, workspaceId?: string) =>
    apiFetch<Connection[]>(`/connections${workspaceId ? `?workspace_id=${workspaceId}` : ""}`, {}, token),
  createConnection: (token: string, payload: Partial<Connection> & { uri: string }) =>
    apiFetch<Connection>("/connections", { method: "POST", body: JSON.stringify(payload) }, token),
  testConnection: (token: string, id: string) => apiFetch<{ ok: boolean; message: string }>(`/connections/${id}/test`, { method: "POST" }, token),
  schema: (token: string, id?: string) => apiFetch<Record<string, unknown>>(`/schema${id ? `?connection_id=${id}` : ""}`, {}, token),
  ask: (token: string, payload: { workspace_id: string; question: string; connection_id?: string; engine?: string; execute?: boolean }) =>
    apiFetch<QueryResult>("/ai/ask", { method: "POST", body: JSON.stringify(payload) }, token),
  history: (token: string, workspaceId?: string) => apiFetch<Record<string, unknown>[]>(`/queries/history${workspaceId ? `?workspace_id=${workspaceId}` : ""}`, {}, token),
  dashboards: (token: string, workspaceId: string) => apiFetch<Record<string, unknown>[]>(`/dashboards?workspace_id=${workspaceId}`, {}, token),
  createDashboard: (token: string, payload: Record<string, unknown>) =>
    apiFetch<Record<string, unknown>>("/dashboards", { method: "POST", body: JSON.stringify(payload) }, token),
  updateDashboard: (token: string, id: string, payload: Record<string, unknown>) =>
    apiFetch<Record<string, unknown>>(`/dashboards/${id}`, { method: "PUT", body: JSON.stringify(payload) }, token),
  duplicateDashboard: (token: string, id: string, workspaceId: string) =>
    apiFetch<Record<string, unknown>>(`/dashboards/${id}/duplicate?workspace_id=${workspaceId}`, { method: "POST" }, token),
  deleteDashboard: (token: string, id: string, workspaceId: string) =>
    apiFetch<Record<string, unknown>>(`/dashboards/${id}?workspace_id=${workspaceId}`, { method: "DELETE" }, token),
  reports: (token: string, workspaceId: string) => apiFetch<Record<string, unknown>[]>(`/reports?workspace_id=${workspaceId}`, {}, token),
  createReport: (token: string, payload: Record<string, unknown>) =>
    apiFetch<Record<string, unknown>>("/reports", { method: "POST", body: JSON.stringify(payload) }, token),
  updateReport: (token: string, id: string, payload: Record<string, unknown>) =>
    apiFetch<Record<string, unknown>>(`/reports/${id}`, { method: "PUT", body: JSON.stringify(payload) }, token),
  downloadReport: (token: string, id: string, workspaceId: string, format: string) =>
    apiBlob(`/reports/${id}/download?workspace_id=${workspaceId}&format=${format}`, token),
  audit: (token: string, workspaceId?: string) => apiFetch<Record<string, unknown>[]>(`/audit-logs${workspaceId ? `?workspace_id=${workspaceId}` : ""}`, {}, token),
  admin: (token: string) => apiFetch<Record<string, unknown>>("/admin/analytics", {}, token),
  agents: (token: string) => apiFetch<{ agents: { node: string; name: string; responsibility: string }[] }>("/admin/agents", {}, token),
  agentTraces: (token: string, workspaceId?: string) =>
    apiFetch<{ traces: AgentWorkflowTrace[]; summary: Record<string, number> }>(`/admin/agents/traces${workspaceId ? `?workspace_id=${workspaceId}` : ""}`, {}, token),
  resources: (token: string, type: string, workspaceId: string) => apiFetch<Record<string, unknown>[]>(`/resources/${type}?workspace_id=${workspaceId}`, {}, token),
  createResource: (token: string, payload: { workspace_id: string; resource_type: string; name: string; payload?: Record<string, unknown> }) =>
    apiFetch<Record<string, unknown>>("/resources", { method: "POST", body: JSON.stringify(payload) }, token),
  notifications: (token: string, workspaceId: string) => apiFetch<Record<string, unknown>[]>(`/resources/notifications/list?workspace_id=${workspaceId}`, {}, token),
  scheduledReports: (token: string, workspaceId: string) => apiFetch<Record<string, unknown>[]>(`/resources/scheduled-reports/list?workspace_id=${workspaceId}`, {}, token),
  createScheduledReport: (token: string, payload: Record<string, unknown>) => apiFetch<Record<string, unknown>>("/resources/scheduled-reports", { method: "POST", body: JSON.stringify(payload) }, token),
  exports: (token: string, workspaceId: string) => apiFetch<Record<string, unknown>[]>(`/resources/exports/list?workspace_id=${workspaceId}`, {}, token),
  createExport: (token: string, payload: Record<string, unknown>) => apiFetch<Record<string, unknown>>("/resources/exports", { method: "POST", body: JSON.stringify(payload) }, token),
  sourceHealth: (token: string, workspaceId: string) => apiFetch<Record<string, unknown>[]>(`/resources/source-health/list?workspace_id=${workspaceId}`, {}, token),
  usageAnalytics: (token: string, workspaceId: string) => apiFetch<Record<string, unknown>>(`/resources/usage/analytics?workspace_id=${workspaceId}`, {}, token),
  knowledgeDocuments: (token: string, workspaceId: string) => apiFetch<Record<string, unknown>[]>(`/resources/knowledge-documents?workspace_id=${workspaceId}`, {}, token),
  createKnowledgeDocument: (token: string, payload: Record<string, unknown>) => apiFetch<Record<string, unknown>>("/resources/knowledge-documents", { method: "POST", body: JSON.stringify(payload) }, token),
  searchKnowledge: (token: string, payload: Record<string, unknown>) => apiFetch<{ query: string; results: Record<string, unknown>[]; search_id: string }>("/resources/knowledge-search", { method: "POST", body: JSON.stringify(payload) }, token),
  connectorCatalog: (token: string) => apiFetch<Record<string, string[]>>("/enterprise/connectors/catalog", {}, token),
  syncHistory: (token: string, workspaceId: string) => apiFetch<Record<string, unknown>[]>(`/enterprise/api/sync-history?workspace_id=${workspaceId}`, {}, token),
  etlRuns: (token: string, workspaceId: string) => apiFetch<Record<string, unknown>[]>(`/enterprise/etl/runs?workspace_id=${workspaceId}`, {}, token),
  realtimeSnapshot: (token: string, workspaceId: string) => apiFetch<Record<string, unknown>>(`/realtime/snapshot?workspace_id=${workspaceId}`, {}, token),
  observabilityMetrics: (token: string) => apiFetch<Record<string, unknown>>("/observability/metrics", {}, token)
  ,
  semanticLayer: (token: string, workspaceId: string) => apiFetch<Record<string, unknown>>(`/resources/semantic-layer?workspace_id=${workspaceId}`, {}, token),
  createSemanticMetric: (token: string, payload: Record<string, unknown>) => apiFetch<Record<string, unknown>>("/resources/semantic-metrics", { method: "POST", body: JSON.stringify(payload) }, token),
  dataLineage: (token: string, workspaceId: string) => apiFetch<Record<string, unknown>>(`/resources/data-lineage?workspace_id=${workspaceId}`, {}, token),
  comments: (token: string, workspaceId: string) => apiFetch<Record<string, unknown>[]>(`/resources/comments/list?workspace_id=${workspaceId}`, {}, token),
  createComment: (token: string, payload: Record<string, unknown>) => apiFetch<Record<string, unknown>>("/resources/comments", { method: "POST", body: JSON.stringify(payload) }, token),
  activityFeed: (token: string, workspaceId: string) => apiFetch<Record<string, unknown>[]>(`/resources/activity-feed?workspace_id=${workspaceId}`, {}, token),
  approvals: (token: string, workspaceId: string) => apiFetch<Record<string, unknown>[]>(`/resources/approvals/list?workspace_id=${workspaceId}`, {}, token),
  requestApproval: (token: string, payload: Record<string, unknown>) => apiFetch<Record<string, unknown>>("/resources/approvals", { method: "POST", body: JSON.stringify(payload) }, token),
  updateResource: (token: string, resourceType: string, resourceId: string, payload: Record<string, unknown>) =>
    apiFetch<Record<string, unknown>>(`/resources/${resourceType}/${resourceId}`, { method: "PUT", body: JSON.stringify(payload) }, token)
};
