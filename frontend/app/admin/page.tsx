"use client";

import { useQuery } from "@tanstack/react-query";
import { Activity, AlertTriangle, BrainCircuit, Database, GitBranch, Users, type LucideIcon } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";

export default function AdminPage() {
  const { token, workspace, user } = useAuthStore();
  const canAdmin = user?.role === "Admin" || user?.role === "Super Admin";
  const analytics = useQuery({ queryKey: ["admin", token], queryFn: () => api.admin(token as string), enabled: Boolean(token && canAdmin) });
  const audit = useQuery({ queryKey: ["audit", token, workspace?.id], queryFn: () => api.audit(token as string, workspace?.id), enabled: Boolean(token && workspace?.id && canAdmin) });
  const agents = useQuery({ queryKey: ["agents", token], queryFn: () => api.agents(token as string), enabled: Boolean(token && canAdmin) });
  const traces = useQuery({ queryKey: ["agent-traces", token, workspace?.id], queryFn: () => api.agentTraces(token as string, workspace?.id), enabled: Boolean(token && workspace?.id && canAdmin) });
  const items: [string, unknown, LucideIcon][] = [
    ["Users", analytics.data?.users, Users],
    ["Connections", analytics.data?.connections, Database],
    ["AI usage logs", analytics.data?.ai_usage_events, Activity],
    ["Failed queries", analytics.data?.failed_queries, AlertTriangle],
    ["Agent workflows", traces.data?.summary?.workflows, BrainCircuit],
    ["Agent invocations", traces.data?.summary?.agent_invocations, GitBranch]
  ];
  return (
    <AppShell title="Admin Panel">
      {!canAdmin ? (
        <Card>
          <CardHeader><CardTitle>Admin access required</CardTitle></CardHeader>
          <CardContent className="text-sm text-muted">Your current role cannot access system analytics, audit logs, or workspace administration.</CardContent>
        </Card>
      ) : (
      <>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-6">
        {items.map(([label, value, Icon]) => (
          <Card key={String(label)}>
            <CardContent className="flex items-center justify-between">
              <div>
                <div className="text-sm text-muted">{String(label)}</div>
                <div className="mt-2 text-2xl font-semibold">{String(value ?? 0)}</div>
              </div>
              <Icon className="text-brand" size={22} />
            </CardContent>
          </Card>
        ))}
      </div>
      <div className="mt-6 grid gap-4 xl:grid-cols-[0.8fr_1.2fr]">
        <Card>
          <CardHeader><CardTitle>System health</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {Object.entries((analytics.data?.system_health as Record<string, string> | undefined) ?? {}).map(([key, value]) => (
              <div className="flex items-center justify-between rounded-md border border-line p-3" key={key}>
                <span className="text-sm font-medium">{key}</span>
                <Badge>{value}</Badge>
              </div>
            ))}
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Audit log</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {(audit.data ?? []).map((item) => (
              <div className="rounded-md border border-line p-3" key={String(item.id)}>
                <div className="text-sm font-medium">{String(item.action)}</div>
                <div className="text-xs text-muted">{String(item.entity_type)} - {String(item.created_at)}</div>
              </div>
            ))}
            {!audit.data?.length && <div className="text-sm text-muted">Audit events appear after login, query, dashboard, and report actions.</div>}
          </CardContent>
        </Card>
      </div>
      <div className="mt-6 grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
        <Card>
          <CardHeader><CardTitle>Agent registry</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {(agents.data?.agents ?? []).map((agent) => (
              <div className="rounded-md border border-line p-3" key={agent.node}>
                <div className="text-sm font-medium">{agent.name}</div>
                <div className="mt-1 text-xs leading-5 text-muted">{agent.responsibility}</div>
              </div>
            ))}
            {!agents.data?.agents?.length && <div className="text-sm text-muted">Agents appear after the registry loads.</div>}
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Agent monitoring</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            {(traces.data?.traces ?? []).slice(0, 5).map((trace) => (
              <div className="rounded-md border border-line p-3" key={trace.id}>
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="text-sm font-medium">{trace.question ?? "Workflow trace"}</div>
                    <div className="mt-1 text-xs text-muted">{trace.intent ?? "intent"} - {trace.engine ?? "engine"}</div>
                  </div>
                  <Badge>{Math.round((trace.final_confidence ?? 0) * 100)}%</Badge>
                </div>
                <div className="mt-3 grid gap-2 text-xs text-muted md:grid-cols-3">
                  <span>Agents: {trace.agent_trace?.length ?? 0}</span>
                  <span>Retries: {trace.retries ?? 0}</span>
                  <span>Tokens: {(trace.token_usage?.prompt ?? 0) + (trace.token_usage?.completion ?? 0)}</span>
                </div>
                <div className="mt-3 grid gap-2 text-xs text-muted md:grid-cols-4">
                  <span>Quality: {trace.agent_outputs?.data_quality?.quality_score ?? "n/a"}</span>
                  <span>Anomaly: {trace.agent_outputs?.anomaly_detection?.severity ?? "n/a"}</span>
                  <span>ETL: {trace.agent_outputs?.etl?.import_status ?? "n/a"}</span>
                  <span>Cost: {trace.agent_outputs?.cost_governance?.query_cost_score ?? "n/a"}</span>
                </div>
                <div className="mt-3 flex flex-wrap gap-2">
                  {(trace.execution_order ?? []).slice(0, 10).map((agent) => <Badge key={`${trace.id}-${agent}`}>{agent}</Badge>)}
                </div>
                {!!trace.errors?.length && <div className="mt-3 text-xs text-danger">{trace.errors.join(", ")}</div>}
              </div>
            ))}
            {!traces.data?.traces?.length && <div className="text-sm text-muted">Run an AI chat workflow to populate agent traces, latency, tokens, retries, and confidence.</div>}
          </CardContent>
        </Card>
      </div>
      </>
      )}
    </AppShell>
  );
}
