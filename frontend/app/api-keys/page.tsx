"use client";

import { FormEvent, useState } from "react";
import { KeyRound } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";

export default function ApiKeysPage() {
  const { token, workspace } = useAuthStore();
  const [name, setName] = useState("Server integration key");
  const [message, setMessage] = useState("");
  const keys = useQuery({ queryKey: ["api-keys", token, workspace?.id], queryFn: () => api.resources(token as string, "api-keys", workspace?.id as string), enabled: Boolean(token && workspace?.id) });

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!token || !workspace) return;
    await api.createResource(token, { workspace_id: workspace.id, resource_type: "api-keys", name, payload: { masked_key: "sk_live_***", status: "placeholder" } });
    setMessage("API key placeholder created.");
    keys.refetch();
  }

  return (
    <AppShell title="API Keys">
      <Card>
        <CardHeader><CardTitle>Create API key</CardTitle></CardHeader>
        <CardContent>
          <form className="flex flex-col gap-3 md:flex-row" onSubmit={submit}>
            <Input value={name} onChange={(event) => setName(event.target.value)} />
            <Button type="submit"><KeyRound size={16} /> Create key</Button>
          </form>
          {message && <p className="mt-3 text-sm text-muted">{message}</p>}
        </CardContent>
      </Card>
      <div className="mt-4 grid gap-3">
        {(keys.data ?? []).map((item) => (
          <Card key={String(item.id)}>
            <CardContent className="flex items-center justify-between">
              <div>
                <div className="font-medium">{String(item.name)}</div>
                <div className="text-sm text-muted">Credentials are masked and never returned in full.</div>
              </div>
              <span className="text-sm text-muted">sk_live_***</span>
            </CardContent>
          </Card>
        ))}
      </div>
    </AppShell>
  );
}
