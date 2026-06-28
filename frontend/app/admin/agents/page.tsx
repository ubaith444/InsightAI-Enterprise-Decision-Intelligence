"use client";

import { useQuery } from "@tanstack/react-query";
import { Activity, GitBranch, Timer } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";

export default function AgentMonitoringPage() {
  const { token, workspace, user } = useAuthStore();
  const canAdmin = user?.role === "Admin" || user?.role === "Super Admin";
  const agents = useQuery({ queryKey: ["agents", token], queryFn: () => api.agents(token as string), enabled: Boolean(token && canAdmin) });
  const traces = useQuery({ queryKey: ["agent-traces-dedicated", token, workspace?.id], queryFn: () => api.agentTraces(token as string, workspace?.id), enabled: Boolean(token && workspace?.id && canAdmin) });
  if (!canAdmin) {
    return <AppShell title="Agent Monitoring"><Card><CardContent className="text-sm text-muted">Admin access required.</CardContent></Card></AppShell>;
  }
  return (
    <AppShell title="Agent Monitoring">
      <div className="grid gap-4 md:grid-cols-3">
        <Card><CardContent><div className="text-sm text-muted">Registered agents</div><div className="mt-2 text-2xl font-semibold">{agents.data?.agents.length ?? 0}</div></CardContent></Card>
        <Card><CardContent><div className="text-sm text-muted">Workflows</div><div className="mt-2 text-2xl font-semibold">{traces.data?.summary?.workflows ?? 0}</div></CardContent></Card>
        <Card><CardContent><div className="text-sm text-muted">Success rate</div><div className="mt-2 text-2xl font-semibold">{Math.round(Number(traces.data?.summary?.success_rate ?? 0) * 100)}%</div></CardContent></Card>
      </div>
      <div className="mt-4 space-y-4">
        {(traces.data?.traces ?? []).slice(0, 8).map((trace) => (
          <Card key={trace.id}>
            <CardHeader><CardTitle>{trace.question ?? "Workflow trace"}</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              <div className="grid gap-2 text-sm text-muted md:grid-cols-4">
                <span><Activity size={14} /> {trace.agent_trace?.length ?? 0} invocations</span>
                <span><Timer size={14} /> {trace.agent_trace?.reduce((sum, item) => sum + Number(item.latency_ms ?? 0), 0).toFixed(1)} ms</span>
                <span>Retries: {trace.retries ?? 0}</span>
                <span>Tokens: {(trace.token_usage?.prompt ?? 0) + (trace.token_usage?.completion ?? 0)}</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {(trace.execution_order ?? []).map((agent) => <Badge key={`${trace.id}-${agent}`}><GitBranch size={12} /> {agent}</Badge>)}
              </div>
              <div className="grid gap-2 text-xs text-muted md:grid-cols-4">
                <span>Cost score: {trace.agent_outputs?.cost_governance?.query_cost_score ?? "n/a"}</span>
                <span>Quality: {trace.agent_outputs?.data_quality?.quality_score ?? "n/a"}</span>
                <span>Anomaly: {trace.agent_outputs?.anomaly_detection?.severity ?? "n/a"}</span>
                <span>Executive confidence: {String((trace.agent_outputs as Record<string, any> | undefined)?.executive_decision?.confidence_score ?? "n/a")}</span>
                <span>Semantic metrics: {trace.agent_outputs?.semantic_layer?.metric_count ?? "n/a"}</span>
                <span>Lineage KPIs: {trace.agent_outputs?.data_lineage?.affected_kpis?.length ?? "n/a"}</span>
                <span>Approval gate: {trace.agent_outputs?.collaboration?.human_in_the_loop ? "enabled" : "n/a"}</span>
                <span>Monitoring: {trace.agent_outputs?.monitoring?.agent_status ?? "n/a"}</span>
                <span>Model: {trace.agent_outputs?.model_route?.selected_model ?? "n/a"}</span>
                <span>Governance: {trace.agent_outputs?.governance?.decision ?? "n/a"}</span>
                <span>Planner: {trace.agent_outputs?.workflow_plan?.fallback_path ? "ready" : "n/a"}</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </AppShell>
  );
}
