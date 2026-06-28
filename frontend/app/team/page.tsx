"use client";

import { useQuery } from "@tanstack/react-query";
import { Users } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";

export default function TeamPage() {
  const { token, workspace, user } = useAuthStore();
  const team = useQuery({ queryKey: ["team", token, workspace?.id], queryFn: () => api.resources(token as string, "team", workspace?.id as string), enabled: Boolean(token && workspace?.id) });
  return (
    <AppShell title="Team Management">
      <Card>
        <CardHeader><CardTitle>Workspace members</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center justify-between rounded-md border border-line p-3">
            <div className="flex items-center gap-3">
              <Users size={18} className="text-brand" />
              <div>
                <div className="font-medium">{user?.full_name ?? "Current user"}</div>
                <div className="text-sm text-muted">{user?.email}</div>
              </div>
            </div>
            <Badge>{user?.role ?? "Role"}</Badge>
          </div>
          {(team.data ?? []).map((item) => (
            <div className="rounded-md border border-line p-3" key={String(item.id)}>
              <div className="font-medium">{String(item.name)}</div>
              <div className="text-sm text-muted">Invitation and role-management placeholder.</div>
            </div>
          ))}
        </CardContent>
      </Card>
    </AppShell>
  );
}
