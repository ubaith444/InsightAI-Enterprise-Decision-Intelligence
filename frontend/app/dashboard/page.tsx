"use client";

import { useQuery } from "@tanstack/react-query";
import { Activity, BarChart3, Database, Gauge, Sparkles, type LucideIcon } from "lucide-react";
import Link from "next/link";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";

export default function DashboardHome() {
  const { token, workspace } = useAuthStore();
  const admin = useQuery({ queryKey: ["admin", token], queryFn: () => api.admin(token as string), enabled: Boolean(token) });
  const history = useQuery({
    queryKey: ["history", token, workspace?.id],
    queryFn: () => api.history(token as string, workspace?.id),
    enabled: Boolean(token && workspace?.id)
  });

  const metrics: [string, unknown, LucideIcon][] = [
    ["Users", admin.data?.users ?? 1, Activity],
    ["Workspaces", admin.data?.workspaces ?? 1, Gauge],
    ["Connections", admin.data?.connections ?? 1, Database],
    ["Query logs", admin.data?.query_logs ?? history.data?.length ?? 0, BarChart3]
  ];

  return (
    <AppShell title="Dashboard Home" actions={<Link href="/chat"><Button size="sm"><Sparkles size={15} /> Ask AI</Button></Link>}>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {metrics.map(([label, value, Icon]) => (
          <Card key={String(label)}>
            <CardContent className="flex items-center justify-between">
              <div>
                <div className="text-sm text-muted">{String(label)}</div>
                <div className="mt-2 text-2xl font-semibold">{String(value)}</div>
              </div>
              <Icon className="text-brand" size={22} />
            </CardContent>
          </Card>
        ))}
      </div>
      <div className="mt-6 grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
        <Card>
          <CardHeader><CardTitle>Workspace Command Center</CardTitle></CardHeader>
          <CardContent className="grid gap-3 md:grid-cols-3">
            {[
              ["Ask revenue by month", "/chat"],
              ["Connect a database", "/connections"],
              ["Generate report", "/reports"]
            ].map(([label, href]) => (
              <Link key={label} href={href} className="rounded-md border border-line p-4 hover:bg-surface">
                <div className="font-medium">{label}</div>
                <div className="mt-2 text-sm text-muted">Open workflow</div>
              </Link>
            ))}
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Recent Query Activity</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {(history.data ?? []).slice(0, 5).map((item) => (
              <div key={String(item.id)} className="rounded-md border border-line p-3">
                <div className="text-sm font-medium">{String(item.question)}</div>
                <div className="text-xs text-muted">{String(item.status)} · {String(item.row_count)} rows</div>
              </div>
            ))}
            {!history.data?.length && <div className="text-sm text-muted">Ask your first question to populate query history.</div>}
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
