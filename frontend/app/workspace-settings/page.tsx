"use client";

import { FormEvent, useState } from "react";
import { Save } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input, Select } from "@/components/ui/input";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";

export default function WorkspaceSettingsPage() {
  const { token, workspace } = useAuthStore();
  const [message, setMessage] = useState("");
  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!token || !workspace) return;
    await api.createResource(token, { workspace_id: workspace.id, resource_type: "workspace-settings", name: "Safety policy", payload: { query_policy: "strict", retention: "365 days" } });
    setMessage("Workspace settings saved.");
  }
  return (
    <AppShell title="Workspace Settings">
      <Card>
        <CardHeader><CardTitle>Controls</CardTitle></CardHeader>
        <CardContent>
          <form className="space-y-3" onSubmit={submit}>
            <Input defaultValue={workspace?.name ?? "Workspace"} />
            <Select defaultValue="strict">
              <option value="strict">Strict read-only query safety</option>
              <option value="review">Manual approval before execution</option>
            </Select>
            <Button type="submit"><Save size={16} /> Save workspace settings</Button>
          </form>
          {message && <p className="mt-3 text-sm text-muted">{message}</p>}
        </CardContent>
      </Card>
    </AppShell>
  );
}
