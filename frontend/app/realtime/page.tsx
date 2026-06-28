"use client";

import { useQuery } from "@tanstack/react-query";
import { Activity, RefreshCw } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";

export default function RealtimePage() {
  const { token, workspace } = useAuthStore();
  const snapshot = useQuery({ queryKey: ["realtime", token, workspace?.id], queryFn: () => api.realtimeSnapshot(token as string, workspace?.id as string), enabled: Boolean(token && workspace?.id), refetchInterval: 15000 });
  const kpis = (snapshot.data?.kpis as Record<string, unknown> | undefined) ?? {};
  return (
    <AppShell title="Realtime Analytics" actions={<Button size="sm" onClick={() => snapshot.refetch()}><RefreshCw size={15} /> Refresh</Button>}>
      <div className="grid gap-4 md:grid-cols-4">
        {[
          ["Questions", kpis.ai_questions_asked ?? 0],
          ["Executed", kpis.queries_executed ?? 0],
          ["Reports", kpis.reports_generated ?? 0],
          ["Failures", kpis.failed_queries ?? 0]
        ].map(([label, value]) => (
          <Card key={String(label)}><CardContent><div className="text-sm text-muted">{String(label)}</div><div className="mt-2 text-2xl font-semibold">{String(value)}</div></CardContent></Card>
        ))}
      </div>
      <Card className="mt-4">
        <CardHeader><CardTitle>Live stream</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center gap-2 text-sm text-muted"><Activity size={16} /> WebSocket endpoint ready at `/api/v1/realtime/ws/{workspace?.id ?? "workspace"}`</div>
          <div className="flex flex-wrap gap-2">{([5, 15, 30, 60]).map((interval) => <Badge key={interval}>{interval}s</Badge>)}</div>
        </CardContent>
      </Card>
    </AppShell>
  );
}
