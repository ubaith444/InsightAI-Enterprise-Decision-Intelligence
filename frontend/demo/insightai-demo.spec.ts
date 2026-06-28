import { expect, test, type Page } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

const API_URL = "http://127.0.0.1:8000/api/v1";
const DEMO_VIDEO = path.resolve(__dirname, "../../docs/assets/demos/insightai-demo.webm");

async function chapter(page: Page, title: string, subtitle: string) {
  await page.evaluate(
    ({ title, subtitle }) => {
      const old = document.querySelector("[data-demo-chapter]");
      old?.remove();
      const el = document.createElement("div");
      el.setAttribute("data-demo-chapter", "true");
      el.innerHTML = `<div style="font-size:12px;letter-spacing:0;text-transform:uppercase;color:#7dd3fc;margin-bottom:6px;">InsightAI demo</div><div style="font-size:28px;font-weight:700;line-height:1.15;">${title}</div><div style="font-size:14px;color:#d1d5db;margin-top:8px;max-width:560px;">${subtitle}</div>`;
      Object.assign(el.style, {
        position: "fixed",
        left: "24px",
        bottom: "24px",
        zIndex: "99999",
        maxWidth: "640px",
        padding: "18px 20px",
        color: "white",
        background: "rgba(10, 15, 28, 0.92)",
        border: "1px solid rgba(255,255,255,0.16)",
        borderRadius: "8px",
        boxShadow: "0 18px 50px rgba(0,0,0,0.35)",
        pointerEvents: "none",
        fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
      });
      document.body.appendChild(el);
    },
    { title, subtitle }
  );
  await page.waitForTimeout(3200);
}

async function pause(page: Page, ms = 2200) {
  await page.waitForTimeout(ms);
}

async function api(token: string, pathName: string, init: RequestInit = {}) {
  const response = await fetch(`${API_URL}${pathName}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...(init.headers || {}),
    },
  });
  if (!response.ok) throw new Error(`${pathName}: ${response.status} ${await response.text()}`);
  return response.json();
}

test("record InsightAI enterprise walkthrough", async ({ page }) => {
  test.setTimeout(300_000);
  fs.mkdirSync(path.dirname(DEMO_VIDEO), { recursive: true });

  await page.goto("/login");
  await chapter(page, "User Login", "Sign in with seeded enterprise credentials and enter the workspace command center.");
  await page.getByPlaceholder("Email").fill("admin@insightai.ai");
  await page.getByPlaceholder("Password").fill("InsightAI123");
  await page.getByRole("button", { name: "Login", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Dashboard Home" })).toBeVisible();
  await pause(page);

  const token = await page.evaluate(() => window.localStorage.getItem("insightai_token") || "");
  const workspaces = await api(token, "/workspaces");
  const activeWorkspace = workspaces[0];
  const workspace = await api(token, "/workspaces", { method: "POST", body: JSON.stringify({ name: `Demo Video Workspace ${Date.now()}` }) });
  await chapter(page, "Workspace Creation", `Created workspace: ${workspace.name}. InsightAI scopes users, dashboards, reports, settings, and audit events by workspace.`);

  await page.goto("/connections");
  await chapter(page, "Database Connection", "Add a read-only analytics connection. Credentials are masked in the frontend and encrypted at rest.");
  await page.getByPlaceholder("Warehouse name").fill(`Demo Video PostgreSQL ${Date.now()}`);
  await page.getByPlaceholder("Database URI").fill("sqlite:///./insightai.db");
  await page.getByPlaceholder("Selected tables or collections").fill("sales, customers, products, orders, inventory");
  await page.getByRole("button", { name: "Add database" }).click();
  await expect(page.getByText("Connection created and audit logged.")).toBeVisible();
  await pause(page);

  await api(token, "/enterprise/api/sync", {
    method: "POST",
    body: JSON.stringify({ workspace_id: activeWorkspace.id, url: "http://127.0.0.1:8000/health" }),
  }).catch(() => undefined);
  await page.goto("/integrations");
  await chapter(page, "Live Data Synchronization", "The integration layer tracks REST sync history, provider metadata, retry strategy, and ETL import runs.");
  await expect(page.getByText("Connector catalog")).toBeVisible();
  await pause(page);

  await page.goto("/chat");
  await chapter(page, "Natural Language Analytics", "Ask a business question in plain English and let InsightAI generate a safe analytical workflow.");
  await page.getByRole("textbox").fill("Show monthly revenue trend for the last 12 months");
  await page.getByRole("button", { name: "Generate and run" }).click();
  await expect(page.getByText("Query validated and executed.")).toBeVisible();
  await chapter(page, "AI Query Generation", "InsightAI shows the generated read-only query, risk, confidence, chart, and AI insights before saving outputs.");
  await expect(page.getByTestId("query-chart")).toBeVisible();
  await pause(page);

  await chapter(page, "Multi-Agent Workflow Execution", "The LangGraph Supervisor routes Planner, Model Router, RAG, Query, Governance, Monitoring, and Insight agents.");
  await page.getByRole("button", { name: "Save to dashboard" }).click();
  await expect(page.getByText("Saved to dashboard.")).toBeVisible();

  await page.goto("/dashboards");
  await chapter(page, "Dashboard Creation", "Charts generated from AI results persist into dashboard storage and are shared with the workspace.");
  await page.getByRole("button", { name: "Create dashboard" }).click();
  await expect(page.getByText("Dashboard page created in MongoDB storage.")).toBeVisible();
  await pause(page);

  await page.goto("/reports");
  await chapter(page, "Executive Report Generation", "Generate executive, weekly, monthly, and sales reports with KPI, chart, and AI explanation sections.");
  await page.getByRole("button", { name: "Generate" }).click();
  await expect(page.getByText("Report generated and audit logged.")).toBeVisible();
  await chapter(page, "Report Export", "Reports download through backend export endpoints for PDF, Excel, CSV, and PowerPoint formats.");
  await page.getByRole("button", { name: "PDF" }).first().click();
  await expect(page.getByText("PDF export downloaded.")).toBeVisible();

  await page.goto("/lineage");
  await chapter(page, "Data Lineage Visualization", "Lineage shows sources, semantic KPIs, dependency edges, and downstream dashboard/report impact.");
  await expect(page.getByRole("heading", { name: "Data Lineage" })).toBeVisible();
  await pause(page);

  await page.goto("/collaboration");
  await chapter(page, "Human Approval Workflow", "Approval gates protect publishing, external actions, report sending, dataset deletion, and major ETL changes.");
  await page.getByRole("button", { name: "Add comment" }).click();
  await expect(page.getByText("@finance Please review this dashboard before publishing.")).toBeVisible();
  await page.getByRole("button", { name: "Request publish approval" }).click();
  await expect(page.getByText("publish_dashboard: pending")).toBeVisible();

  await page.goto("/admin/agents");
  await chapter(page, "Agent Monitoring Dashboard", "Admins inspect agent registry, execution timelines, retries, tokens, model routing, governance, and observability spans.");
  await expect(page.getByText("Registered agents")).toBeVisible();
  await pause(page);

  await page.goto("/admin");
  await chapter(page, "Audit Logs", "Login, connection, query, dashboard, report, approval, and admin events are captured for governance.");
  await expect(page.getByRole("heading", { name: "Audit log" })).toBeVisible();
  await pause(page);

  await page.goto("/realtime");
  await chapter(page, "Real-Time KPI Updates", "Realtime analytics expose refresh controls, KPI cards, WebSocket readiness, and live-stream intervals.");
  await page.getByRole("button", { name: "Refresh" }).click();
  await expect(page.getByText("Live stream")).toBeVisible();
  await pause(page);

  await page.goto("/settings");
  await chapter(page, "Settings & RBAC", "Workspace settings persist to the backend, and Admin-only navigation is role-gated by RBAC.");
  await page.getByRole("button", { name: "Save settings" }).click();
  await expect(page.getByText("Workspace settings saved to backend storage.")).toBeVisible();
  await pause(page, 2800);

  await page.evaluate(() => document.querySelector("[data-demo-chapter]")?.remove());
});

test.afterEach(async ({ page }, testInfo) => {
  const video = page.video();
  if (!video) return;
  if (testInfo.status === "passed") {
    await page.close();
    await video.saveAs(DEMO_VIDEO);
  }
});
