"use client";

import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Save } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input, Select } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { useAuthStore } from "@/stores/auth-store";
import { api } from "@/lib/api";

export default function SettingsPage() {
  const { token, user, workspace } = useAuthStore();
  const queryClient = useQueryClient();
  const [message, setMessage] = useState("");
  const [safetyMode, setSafetyMode] = useState("strict");
  const settings = useQuery({
    queryKey: ["settings-resource", token, workspace?.id],
    queryFn: () => api.resources(token as string, "workspace-settings", workspace?.id as string),
    enabled: Boolean(token && workspace?.id)
  });
  const saveSettings = useMutation({
    mutationFn: () => api.createResource(token as string, {
      workspace_id: workspace?.id as string,
      resource_type: "workspace-settings",
      name: "Workspace controls",
      payload: {
        workspace_name: workspace?.name,
        query_safety: safetyMode,
        approvals_required_for: ["publishing_dashboards", "sending_reports", "external_actions", "deleting_datasets"],
        notifications: true,
        memory: true,
        audit_settings: "immutable_append_only"
      }
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["settings-resource"] });
      setMessage("Workspace settings saved to backend storage.");
    }
  });

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    saveSettings.mutate();
  }

  return (
    <AppShell title="Settings">
      <div className="grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
        <Card>
          <CardHeader><CardTitle>Workspace settings</CardTitle></CardHeader>
          <CardContent>
            <form className="space-y-3" onSubmit={submit}>
              <Input defaultValue={workspace?.name ?? "InsightAI Workspace"} />
              <Select value={safetyMode} onChange={(event) => setSafetyMode(event.target.value)}>
                <option value="strict">Strict query safety</option>
                <option value="review">Manual review before execution</option>
              </Select>
              <Button type="submit" disabled={saveSettings.isPending}><Save size={16} /> Save settings</Button>
            </form>
            {message && <p className="mt-4 text-sm text-muted">{message}</p>}
            <div className="mt-4 space-y-2">
              {(settings.data ?? []).slice(0, 4).map((item) => (
                <div key={String(item.id)} className="rounded-md border border-line p-3 text-sm text-muted">{String(item.name)} saved</div>
              ))}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Security and roles</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between rounded-md border border-line p-3">
              <div>
                <div className="font-medium">{user?.full_name ?? "Current user"}</div>
                <div className="text-sm text-muted">{user?.email}</div>
              </div>
              <Badge>{user?.role ?? "Role"}</Badge>
            </div>
            <Button variant="secondary" onClick={() => setMessage("Role changes require Admin approval and are recorded in audit logs.")}>Request role review</Button>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
