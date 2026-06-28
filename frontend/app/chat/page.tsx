"use client";

import { FormEvent, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Play, Save, ShieldCheck } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { AutoChart } from "@/components/charts/auto-chart";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, Textarea } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";
import type { QueryResult } from "@/types";

const examples = [
  "Show revenue by month",
  "Find top 10 customers",
  "Compare sales between regions",
  "Analyze products with low sales",
  "Generate MongoDB aggregation for customer activity"
];

export default function ChatPage() {
  const { token, workspace } = useAuthStore();
  const [question, setQuestion] = useState(examples[0]);
  const [engine, setEngine] = useState("sql");
  const [result, setResult] = useState<QueryResult | null>(null);
  const [message, setMessage] = useState("");
  const connections = useQuery({ queryKey: ["connections", token, workspace?.id], queryFn: () => api.connections(token as string, workspace?.id), enabled: Boolean(token && workspace?.id) });
  const [connectionId, setConnectionId] = useState<string>("");

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!token || !workspace) return;
    setMessage("Generating safe query...");
    const response = await api.ask(token, { workspace_id: workspace.id, question, connection_id: connectionId || undefined, engine, execute: true });
    setResult(response);
    setMessage(!response.generated_query && response.rows.length === 0 ? "Clarification required." : response.safe ? "Query validated and executed." : "Query failed safety or execution checks.");
  }

  async function saveToDashboard() {
    if (!token || !workspace || !result) return;
    await api.createDashboard(token, {
      workspace_id: workspace.id,
      name: `Saved: ${result.question}`,
      widgets: [{ title: result.question, chart: result.chart, rows: result.rows }],
      shared_with: []
    });
    setMessage("Saved to dashboard.");
  }

  return (
    <AppShell title="AI Data Chat">
      <div className="grid gap-4 xl:grid-cols-[0.95fr_1.05fr]">
        <Card>
          <CardHeader><CardTitle>Ask InsightAI</CardTitle></CardHeader>
          <CardContent>
            <form className="space-y-4" onSubmit={submit}>
              <Textarea value={question} onChange={(event) => setQuestion(event.target.value)} />
              <div className="grid gap-3 md:grid-cols-2">
                <Select value={engine} onChange={(event) => setEngine(event.target.value)}>
                  <option value="sql">SQL</option>
                  <option value="mongodb">MongoDB aggregation</option>
                </Select>
                <Select value={connectionId} onChange={(event) => setConnectionId(event.target.value)}>
                  <option value="">Demo warehouse</option>
                  {(connections.data ?? []).map((connection) => <option key={connection.id} value={connection.id}>{connection.name}</option>)}
                </Select>
              </div>
              <div className="flex flex-wrap gap-2">
                {examples.map((item) => <Button key={item} type="button" variant="secondary" size="sm" onClick={() => setQuestion(item)}>{item}</Button>)}
              </div>
              <Button type="submit"><Play size={16} /> Generate and run</Button>
            </form>
            {message && <p className="mt-4 text-sm text-muted">{message}</p>}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Result</CardTitle>
              {result && <Badge><ShieldCheck size={13} /> {result.safe ? "Safe" : "Blocked"}</Badge>}
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {result ? (
              <>
                <pre className="max-h-44 overflow-auto rounded-md bg-ink p-3 text-xs text-white">{typeof result.generated_query === "string" ? result.generated_query : JSON.stringify(result.generated_query, null, 2)}</pre>
                <p className="text-sm text-muted">{result.explanation}</p>
                <div className="grid gap-3 rounded-md border border-line p-3 text-sm md:grid-cols-3">
                  <div>
                    <div className="text-xs text-muted">Confidence</div>
                    <div className="font-semibold">{Math.round((result.query_confidence?.confidence_score ?? result.final_confidence ?? 0) * 100)}%</div>
                  </div>
                  <div>
                    <div className="text-xs text-muted">Risk</div>
                    <div className="font-semibold">{result.query_confidence?.risk_level ?? "within_limits"}</div>
                  </div>
                  <div>
                    <div className="text-xs text-muted">Correction</div>
                    <div className="font-semibold">{result.query_confidence?.suggested_corrections?.[0] ?? "No correction required"}</div>
                  </div>
                </div>
                <AutoChart rows={result.rows} chart={result.chart} />
                <div className="grid gap-3 md:grid-cols-2">
                  <InsightBlock title="Summary" items={[result.insights.summary]} />
                  <InsightBlock title="Recommendations" items={result.insights.recommendations} />
                </div>
                <Button variant="secondary" onClick={saveToDashboard}><Save size={16} /> Save to dashboard</Button>
              </>
            ) : (
              <div className="rounded-md border border-dashed border-line p-8 text-center text-sm text-muted">Generated query, chart, table, and insights appear here.</div>
            )}
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}

function InsightBlock({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="rounded-md border border-line p-3">
      <div className="text-sm font-medium">{title}</div>
      <ul className="mt-2 space-y-1 text-sm text-muted">
        {items.map((item) => <li key={item}>{item}</li>)}
      </ul>
    </div>
  );
}
