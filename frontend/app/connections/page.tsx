"use client";

import { FormEvent, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Database, PlugZap } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input, Select } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";

export default function ConnectionsPage() {
  const { token, workspace } = useAuthStore();
  const [message, setMessage] = useState("");
  const connections = useQuery({ queryKey: ["connections", token, workspace?.id], queryFn: () => api.connections(token as string, workspace?.id), enabled: Boolean(token && workspace?.id) });

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !workspace) {
      setMessage("Workspace is still loading. Try again in a moment.");
      return;
    }
    const formElement = event.currentTarget;
    const form = new FormData(formElement);
    setMessage("Adding connection...");
    try {
      await api.createConnection(token, {
        workspace_id: workspace.id,
        name: String(form.get("name")),
        kind: String(form.get("kind")) as "postgresql",
        uri: String(form.get("uri")),
        is_read_only: form.get("read_only") === "on",
        selected_assets: String(form.get("assets")).split(",").map((item) => item.trim()).filter(Boolean)
      });
      formElement.reset();
      await connections.refetch();
      setMessage("Connection created and audit logged.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Connection could not be created.");
    }
  }

  async function test(id: string) {
    if (!token) return;
    const response = await api.testConnection(token, id);
    setMessage(response.message);
  }

  return (
    <AppShell title="Database Connections">
      <div className="grid gap-4 xl:grid-cols-[0.8fr_1.2fr]">
        <Card>
          <CardHeader><CardTitle>Add connection</CardTitle></CardHeader>
          <CardContent>
            <form className="space-y-4" onSubmit={submit}>
              <Input name="name" placeholder="Warehouse name" defaultValue="Finance Postgres" required />
              <Select name="kind" defaultValue="postgresql">
                <option value="postgresql">PostgreSQL</option>
                <option value="mysql">MySQL placeholder</option>
                <option value="sqlite">SQLite placeholder</option>
                <option value="mongodb">MongoDB</option>
              </Select>
              <Input name="uri" placeholder="Database URI" required />
              <Input name="assets" placeholder="Selected tables or collections" defaultValue="sales, customers, products" />
              <label className="flex items-center gap-2 text-sm"><input name="read_only" type="checkbox" defaultChecked /> Mark as read-only</label>
              <Button type="submit"><Database size={16} /> Add database</Button>
            </form>
            {message && <p className="mt-4 text-sm text-muted">{message}</p>}
          </CardContent>
        </Card>
        <div className="space-y-3">
          {(connections.data ?? []).map((connection) => (
            <Card key={connection.id}>
              <CardContent className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                <div>
                  <div className="font-medium">{connection.name}</div>
                  <div className="mt-1 text-sm text-muted">{connection.kind} · {connection.masked_uri} · {connection.selected_assets.join(", ") || "All assets"}</div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge>{connection.is_read_only ? "Read-only" : "Write disabled by policy"}</Badge>
                  <Button variant="secondary" size="sm" onClick={() => test(connection.id)}><PlugZap size={15} /> Test</Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </AppShell>
  );
}
