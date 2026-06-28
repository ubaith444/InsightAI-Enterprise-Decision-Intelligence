"use client";

import { useQuery } from "@tanstack/react-query";
import { GitBranch } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";

export default function LineagePage() {
  const { token, workspace } = useAuthStore();
  const lineage = useQuery({
    queryKey: ["data-lineage", token, workspace?.id],
    queryFn: () => api.dataLineage(token as string, workspace?.id as string),
    enabled: Boolean(token && workspace?.id)
  });
  const nodes = (lineage.data?.nodes as Record<string, unknown>[] | undefined) ?? [];
  const edges = (lineage.data?.edges as Record<string, unknown>[] | undefined) ?? [];
  return (
    <AppShell title="Data Lineage">
      <div className="grid gap-4 md:grid-cols-3">
        <Card><CardContent><div className="text-sm text-muted">Nodes</div><div className="mt-2 text-2xl font-semibold">{nodes.length}</div></CardContent></Card>
        <Card><CardContent><div className="text-sm text-muted">Dependencies</div><div className="mt-2 text-2xl font-semibold">{edges.length}</div></CardContent></Card>
        <Card><CardContent><div className="text-sm text-muted">KPIs</div><div className="mt-2 text-2xl font-semibold">{((lineage.data?.affected_kpis as unknown[]) ?? []).length}</div></CardContent></Card>
      </div>
      <div className="mt-4 grid gap-4 xl:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Dependency graph</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {edges.slice(0, 16).map((edge, index) => (
              <div key={`${edge.from}-${edge.to}-${index}`} className="flex items-center gap-2 rounded-md border border-line p-3 text-sm">
                <GitBranch size={15} />
                <span>{String(edge.from)}</span>
                <Badge>{String(edge.relationship)}</Badge>
                <span>{String(edge.to)}</span>
              </div>
            ))}
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Assets</CardTitle></CardHeader>
          <CardContent className="flex flex-wrap gap-2">
            {nodes.map((node) => <Badge key={String(node.id)}>{String(node.type)}: {String(node.label ?? node.id)}</Badge>)}
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
