"use client";

import { useQuery } from "@tanstack/react-query";
import { FormEvent, useState } from "react";
import { GripVertical, Plus, Share2 } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";

export default function DashboardsPage() {
  const { token, workspace } = useAuthStore();
  const [message, setMessage] = useState("");
  const dashboards = useQuery({ queryKey: ["dashboards", token, workspace?.id], queryFn: () => api.dashboards(token as string, workspace!.id), enabled: Boolean(token && workspace?.id) });

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !workspace) return;
    const form = new FormData(event.currentTarget);
    await api.createDashboard(token, {
      workspace_id: workspace.id,
      name: String(form.get("name")),
      widgets: [
        { title: "Revenue by month", type: "line", position: 1 },
        { title: "Region mix", type: "bar", position: 2 }
      ],
      shared_with: []
    });
    dashboards.refetch();
    setMessage("Dashboard page created in MongoDB storage.");
  }

  return (
    <AppShell title="Dashboard Builder">
      <div className="grid gap-4 xl:grid-cols-[0.75fr_1.25fr]">
        <Card>
          <CardHeader><CardTitle>Create dashboard page</CardTitle></CardHeader>
          <CardContent>
            <form className="space-y-3" onSubmit={submit}>
              <Input name="name" defaultValue="Executive Revenue Board" />
              <Button type="submit"><Plus size={16} /> Create dashboard</Button>
            </form>
            <Button className="mt-3" variant="secondary" onClick={() => setMessage("Drag-and-drop rearranging placeholder: connect dnd-kit for production layout editing.")}><GripVertical size={16} /> Rearrange placeholder</Button>
            {message && <p className="mt-4 text-sm text-muted">{message}</p>}
          </CardContent>
        </Card>
        <div className="space-y-3">
          {(dashboards.data ?? []).map((dashboard) => (
            <Card key={String(dashboard.id)}>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">{String(dashboard.name)}</div>
                    <div className="text-sm text-muted">{Array.isArray(dashboard.widgets) ? dashboard.widgets.length : 0} widgets</div>
                  </div>
                  <Badge><Share2 size={13} /> Workspace shared</Badge>
                </div>
              </CardContent>
            </Card>
          ))}
          {!dashboards.data?.length && <Card><CardContent className="text-sm text-muted">Save a chart from AI Chat or create a dashboard page.</CardContent></Card>}
        </div>
      </div>
    </AppShell>
  );
}
