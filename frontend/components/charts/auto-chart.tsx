"use client";

import { Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const colors = ["#0B5FFF", "#12B886", "#F59E0B", "#E11D48", "#6B7280"];

export function AutoChart({ rows, chart }: { rows: Record<string, string | number | null>[]; chart: { type: string; x?: string; y?: string } }) {
  if (chart.type === "kpi") {
    return (
      <div data-testid="query-chart" className="grid gap-3 md:grid-cols-3">
        {Object.entries(rows[0] ?? {}).filter(([, value]) => typeof value === "number").slice(0, 3).map(([key, value]) => (
          <div key={key} className="rounded-md border border-line p-4">
            <div className="text-xs uppercase text-muted">{key}</div>
            <div className="mt-2 text-2xl font-semibold">{String(value)}</div>
          </div>
        ))}
      </div>
    );
  }
  if (chart.type === "map") {
    return (
      <div data-testid="query-chart" className="grid min-h-[260px] place-items-center rounded-md border border-line bg-surface p-6 text-center">
        <div>
          <div className="text-sm font-semibold">Map placeholder</div>
          <div className="mt-2 text-sm text-muted">Geographic data detected. Production map rendering can be connected to Mapbox or a BI map layer.</div>
        </div>
      </div>
    );
  }
  if (!rows.length || chart.type === "table" || !chart.x || !chart.y) {
    return (
      <div data-testid="query-chart" className="overflow-hidden rounded-md border border-line">
        <table className="w-full text-left text-sm">
          <thead className="bg-surface text-xs uppercase text-muted">
            <tr>{Object.keys(rows[0] ?? { status: "No rows" }).map((key) => <th className="px-3 py-2" key={key}>{key}</th>)}</tr>
          </thead>
          <tbody>
            {rows.slice(0, 8).map((row, index) => (
              <tr className="border-t border-line" key={index}>
                {Object.values(row).map((value, cell) => <td className="px-3 py-2" key={cell}>{String(value)}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }
  if (chart.type === "pie" || chart.type === "donut") {
    return (
      <div data-testid="query-chart" className="h-[300px]">
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie data={rows} dataKey={chart.y} nameKey={chart.x} outerRadius={110} innerRadius={64}>
            {rows.map((_, index) => <Cell key={index} fill={colors[index % colors.length]} />)}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
      </div>
    );
  }
  if (chart.type === "area") {
    return (
      <div data-testid="query-chart" className="h-[300px]">
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={rows}>
          <CartesianGrid stroke="#E5E7EB" vertical={false} />
          <XAxis dataKey={chart.x} tickLine={false} axisLine={false} />
          <YAxis tickLine={false} axisLine={false} />
          <Tooltip />
          <Area type="monotone" dataKey={chart.y} stroke="#0B5FFF" fill="#0B5FFF" strokeWidth={2} />
        </AreaChart>
      </ResponsiveContainer>
      </div>
    );
  }
  if (chart.type === "bar") {
    return (
      <div data-testid="query-chart" className="h-[300px]">
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={rows}>
          <CartesianGrid stroke="#E5E7EB" vertical={false} />
          <XAxis dataKey={chart.x} tickLine={false} axisLine={false} />
          <YAxis tickLine={false} axisLine={false} />
          <Tooltip />
          <Bar dataKey={chart.y} fill="#0B5FFF" />
        </BarChart>
      </ResponsiveContainer>
      </div>
    );
  }
  return (
    <div data-testid="query-chart" className="h-[300px]">
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={rows}>
        <CartesianGrid stroke="#E5E7EB" vertical={false} />
        <XAxis dataKey={chart.x} tickLine={false} axisLine={false} />
        <YAxis tickLine={false} axisLine={false} />
        <Tooltip />
        <Line type="monotone" dataKey={chart.y} stroke="#0B5FFF" strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
    </div>
  );
}
