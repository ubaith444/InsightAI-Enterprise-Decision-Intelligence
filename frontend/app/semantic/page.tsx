"use client";

import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input, Textarea } from "@/components/ui/input";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";

export default function SemanticPage() {
  const { token, workspace, user } = useAuthStore();
  const queryClient = useQueryClient();
  const [name, setName] = useState("Net Revenue");
  const [formula, setFormula] = useState("SUM(sales.revenue) - SUM(discounts)");
  const [definition, setDefinition] = useState("Revenue after discounts and credits.");
  const canAdmin = user?.role === "Admin" || user?.role === "Super Admin";
  const semantic = useQuery({
    queryKey: ["semantic-layer", token, workspace?.id],
    queryFn: () => api.semanticLayer(token as string, workspace?.id as string),
    enabled: Boolean(token && workspace?.id)
  });
  const createMetric = useMutation({
    mutationFn: () => api.createSemanticMetric(token as string, {
      workspace_id: workspace?.id,
      name,
      formula,
      definition,
      owner: "Analytics",
      dimensions: ["month", "region"],
      tags: ["custom"]
    }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["semantic-layer"] })
  });
  const metrics = (semantic.data?.metrics as Record<string, unknown>[] | undefined) ?? [];

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (canAdmin) createMetric.mutate();
  }

  return (
    <AppShell title="Semantic Layer">
      <div className="grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
        <Card>
          <CardHeader><CardTitle>Business metrics</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <div className="text-3xl font-semibold">{Number(semantic.data?.metric_count ?? metrics.length)}</div>
            <p className="text-sm text-muted">Governed metric definitions used by the multi-agent workflow.</p>
            <form className="space-y-3" onSubmit={submit}>
              <Input value={name} onChange={(event) => setName(event.target.value)} disabled={!canAdmin} />
              <Input value={formula} onChange={(event) => setFormula(event.target.value)} disabled={!canAdmin} />
              <Textarea value={definition} onChange={(event) => setDefinition(event.target.value)} disabled={!canAdmin} />
              <Button type="submit" disabled={!canAdmin || createMetric.isPending}><Plus size={16} /> Add metric</Button>
            </form>
            {!canAdmin && <p className="text-sm text-muted">Admin role required to define metrics.</p>}
          </CardContent>
        </Card>
        <div className="space-y-3">
          {metrics.map((metric) => (
            <Card key={String(metric.id ?? metric.name)}>
              <CardContent>
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="font-medium">{String(metric.name)}</div>
                    <div className="mt-1 text-sm text-muted">{String(metric.definition ?? metric.payload ?? "")}</div>
                    <code className="mt-2 block rounded-md bg-surface p-2 text-xs">{String(metric.formula ?? "")}</code>
                  </div>
                  <Badge>{String(metric.owner ?? "Analytics")}</Badge>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </AppShell>
  );
}
