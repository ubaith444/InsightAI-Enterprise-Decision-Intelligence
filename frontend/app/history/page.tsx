"use client";

import { useQuery } from "@tanstack/react-query";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";

export default function HistoryPage() {
  const { token, workspace } = useAuthStore();
  const history = useQuery({ queryKey: ["history", token, workspace?.id], queryFn: () => api.history(token as string, workspace?.id), enabled: Boolean(token && workspace?.id) });
  return (
    <AppShell title="Query History">
      <Card>
        <CardHeader><CardTitle>Generated and executed queries</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          {(history.data ?? []).map((item) => (
            <div key={String(item.id)} className="rounded-md border border-line p-4">
              <div className="flex items-center justify-between gap-3">
                <div className="font-medium">{String(item.question)}</div>
                <Badge>{String(item.status)}</Badge>
              </div>
              <pre className="mt-3 overflow-auto rounded-md bg-surface p-3 text-xs">{String(item.generated_query)}</pre>
            </div>
          ))}
          {!history.data?.length && <div className="text-sm text-muted">No queries yet. Run one from AI Data Chat.</div>}
        </CardContent>
      </Card>
    </AppShell>
  );
}
