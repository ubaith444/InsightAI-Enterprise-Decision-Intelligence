"use client";

import { FormEvent, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Download, FileText } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input, Select } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";

export default function ReportsPage() {
  const { token, workspace } = useAuthStore();
  const [message, setMessage] = useState("");
  const reports = useQuery({ queryKey: ["reports", token, workspace?.id], queryFn: () => api.reports(token as string, workspace!.id), enabled: Boolean(token && workspace?.id) });

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !workspace) return;
    const form = new FormData(event.currentTarget);
    await api.createReport(token, {
      workspace_id: workspace.id,
      title: String(form.get("title")),
      report_type: String(form.get("type")),
      sections: [{ title: "KPIs" }, { title: "Charts" }, { title: "AI explanation" }]
    });
    reports.refetch();
    setMessage("Report generated and audit logged.");
  }

  async function download(reportId: string, format: string) {
    if (!token || !workspace) return;
    await api.downloadReport(token, reportId, workspace.id, format);
    setMessage(`${format.toUpperCase()} export downloaded.`);
  }

  return (
    <AppShell title="Report Generator">
      <div className="grid gap-4 xl:grid-cols-[0.75fr_1.25fr]">
        <Card>
          <CardHeader><CardTitle>Generate report</CardTitle></CardHeader>
          <CardContent>
            <form className="space-y-3" onSubmit={submit}>
              <Input name="title" defaultValue="Weekly Executive Summary" />
              <Select name="type" defaultValue="weekly">
                <option value="weekly">Weekly report</option>
                <option value="monthly">Monthly report</option>
                <option value="sales">Sales report</option>
                <option value="executive">Executive summary</option>
              </Select>
              <Button type="submit" disabled={!workspace}><FileText size={16} /> Generate</Button>
            </form>
            {message && <p className="mt-4 text-sm text-muted">{message}</p>}
          </CardContent>
        </Card>
        <div className="space-y-3">
          {(reports.data ?? []).map((report) => (
            <Card key={String(report.id)}>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">{String(report.title)}</div>
                    <div className="text-sm text-muted">{String(report.report_type)} · KPIs, charts, explanation</div>
                  </div>
                  <div className="flex flex-wrap justify-end gap-2">
                    {["pdf", "excel", "csv", "powerpoint"].map((format) => (
                      <Button key={format} variant="secondary" size="sm" onClick={() => download(String(report.id), format)}>
                        <Download size={14} /> {format.toUpperCase()}
                      </Button>
                    ))}
                    <Badge>Exports ready</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
          {!reports.data?.length && <Card><CardContent className="text-sm text-muted">Generate a weekly, monthly, sales, or executive report.</CardContent></Card>}
        </div>
      </div>
    </AppShell>
  );
}
