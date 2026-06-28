"use client";

import { useQuery } from "@tanstack/react-query";
import { CreditCard } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";

export default function BillingPage() {
  const { token, workspace } = useAuthStore();
  const usage = useQuery({ queryKey: ["usage", token, workspace?.id], queryFn: () => api.usageAnalytics(token as string, workspace?.id as string), enabled: Boolean(token && workspace?.id) });
  return (
    <AppShell title="Usage and Billing">
      <div className="grid gap-4 md:grid-cols-3">
        {([
          ["AI questions", usage.data?.ai_questions_asked ?? 0],
          ["Queries executed", usage.data?.queries_executed ?? 0],
          ["Failed queries", usage.data?.failed_queries ?? 0]
        ] as [string, unknown][]).map(([label, value]) => (
          <Card key={label}>
            <CardContent className="flex items-center justify-between">
              <div>
                <div className="text-sm text-muted">{label}</div>
                <div className="mt-2 text-2xl font-semibold">{String(value)}</div>
              </div>
              <CreditCard className="text-brand" size={20} />
            </CardContent>
          </Card>
        ))}
      </div>
      <Card className="mt-4">
        <CardHeader><CardTitle>Plan</CardTitle></CardHeader>
        <CardContent className="flex items-center justify-between">
          <div>
            <div className="font-medium">Business Intelligence Pro</div>
            <div className="text-sm text-muted">Billing integration placeholder with workspace usage limits.</div>
          </div>
          <Badge>Demo mode</Badge>
        </CardContent>
      </Card>
    </AppShell>
  );
}
