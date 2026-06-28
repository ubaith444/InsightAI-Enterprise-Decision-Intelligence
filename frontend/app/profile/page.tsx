"use client";

import { FormEvent, useState } from "react";
import { Save } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";

export default function ProfilePage() {
  const { token, workspace, user } = useAuthStore();
  const [message, setMessage] = useState("");
  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!token || !workspace) return;
    await api.createResource(token, { workspace_id: workspace.id, resource_type: "profile-settings", name: user?.email ?? "profile", payload: { notifications: "enabled" } });
    setMessage("Profile settings saved.");
  }
  return (
    <AppShell title="Profile Settings">
      <Card>
        <CardHeader><CardTitle>Profile</CardTitle></CardHeader>
        <CardContent>
          <form className="space-y-3" onSubmit={submit}>
            <Input defaultValue={user?.full_name ?? ""} />
            <Input defaultValue={user?.email ?? ""} />
            <Button type="submit"><Save size={16} /> Save profile</Button>
          </form>
          {message && <p className="mt-3 text-sm text-muted">{message}</p>}
        </CardContent>
      </Card>
    </AppShell>
  );
}
