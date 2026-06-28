"use client";

import { useQuery } from "@tanstack/react-query";
import { DatabaseZap, PlugZap } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";

export default function IntegrationsPage() {
  const { token, workspace } = useAuthStore();
  const catalog = useQuery({ queryKey: ["connector-catalog", token], queryFn: () => api.connectorCatalog(token as string), enabled: Boolean(token) });
  const etl = useQuery({ queryKey: ["etl-runs", token, workspace?.id], queryFn: () => api.etlRuns(token as string, workspace?.id as string), enabled: Boolean(token && workspace?.id) });
  const sync = useQuery({ queryKey: ["sync-history", token, workspace?.id], queryFn: () => api.syncHistory(token as string, workspace?.id as string), enabled: Boolean(token && workspace?.id) });
  return (
    <AppShell title="Enterprise Integrations">
      <div className="grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
        <Card>
          <CardHeader><CardTitle>Connector catalog</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            {Object.entries(catalog.data ?? {}).map(([group, items]) => (
              <div key={group} className="rounded-md border border-line p-3">
                <div className="flex items-center gap-2 font-medium"><PlugZap size={16} className="text-brand" /> {group}</div>
                <div className="mt-3 flex flex-wrap gap-2">{items.map((item) => <Badge key={item}>{item}</Badge>)}</div>
              </div>
            ))}
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>ETL and sync monitoring</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {(etl.data ?? []).slice(0, 5).map((run) => (
              <div className="rounded-md border border-line p-3" key={String(run.id)}>
                <div className="flex items-center gap-2 font-medium"><DatabaseZap size={16} className="text-brand" /> {String(run.name)}</div>
                <div className="mt-1 text-sm text-muted">{String(run.import_status)} - {String(run.rows_processed)} rows</div>
              </div>
            ))}
            {(sync.data ?? []).slice(0, 5).map((run) => (
              <div className="rounded-md border border-line p-3" key={String(run.id)}>
                <div className="font-medium">{String(run.name)}</div>
                <div className="mt-1 text-sm text-muted">{String(run.status)} - REST API sync</div>
              </div>
            ))}
            {!etl.data?.length && !sync.data?.length && <div className="text-sm text-muted">ETL imports and API sync history appear here after ingestion jobs run.</div>}
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
