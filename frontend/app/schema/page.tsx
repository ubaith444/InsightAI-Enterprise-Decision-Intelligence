"use client";

import { useQuery } from "@tanstack/react-query";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";

export default function SchemaPage() {
  const { token } = useAuthStore();
  const schema = useQuery({ queryKey: ["schema", token], queryFn: () => api.schema(token as string), enabled: Boolean(token) });
  const tables = (schema.data?.tables as { name: string; columns: { name: string; type: string; nullable: boolean }[] }[] | undefined) ?? [];

  return (
    <AppShell title="Schema Explorer">
      <div className="grid gap-4 lg:grid-cols-2">
        {tables.map((table) => (
          <Card key={table.name}>
            <CardHeader><CardTitle>{table.name}</CardTitle></CardHeader>
            <CardContent>
              <div className="overflow-hidden rounded-md border border-line">
                <table className="w-full text-sm">
                  <thead className="bg-surface text-left text-xs uppercase text-muted">
                    <tr><th className="px-3 py-2">Column</th><th className="px-3 py-2">Type</th><th className="px-3 py-2">Nullable</th></tr>
                  </thead>
                  <tbody>
                    {table.columns.map((column) => (
                      <tr className="border-t border-line" key={column.name}>
                        <td className="px-3 py-2 font-medium">{column.name}</td>
                        <td className="px-3 py-2 text-muted">{column.type}</td>
                        <td className="px-3 py-2 text-muted">{column.nullable ? "Yes" : "No"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        ))}
        {!tables.length && <Card><CardContent className="text-sm text-muted">Schema will appear after the API seed finishes.</CardContent></Card>}
      </div>
    </AppShell>
  );
}
