import { expect, test, type Page } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

const SCREENSHOT_DIR = path.resolve(__dirname, "../../screenshots");

async function login(page: Page) {
  await page.goto("/login");
  await page.getByRole("button", { name: "Login", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Dashboard Home" })).toBeVisible();
}

async function shot(page: Page, name: string) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, name), fullPage: true });
}

test("capture release screenshots", async ({ page }) => {
  await login(page);
  await shot(page, "01-dashboard-home.png");

  await page.goto("/chat");
  await page.getByRole("textbox").fill("Show monthly revenue trend for the last 12 months");
  await page.getByRole("button", { name: "Generate and run" }).click();
  await expect(page.getByText("Query validated and executed.")).toBeVisible();
  await expect(page.getByTestId("query-chart")).toBeVisible();
  await shot(page, "02-ai-data-chat.png");

  await page.goto("/dashboards");
  await expect(page.getByRole("heading", { name: "Dashboard Builder" })).toBeVisible();
  await shot(page, "03-dashboard-builder.png");

  await page.goto("/reports");
  await expect(page.getByRole("heading", { name: "Report Generator" })).toBeVisible();
  await shot(page, "04-report-generator.png");

  await page.goto("/lineage");
  await expect(page.getByRole("heading", { name: "Data Lineage" })).toBeVisible();
  await shot(page, "05-data-lineage.png");

  await page.goto("/admin/agents");
  await expect(page.getByText("Registered agents")).toBeVisible();
  await shot(page, "06-agent-monitoring.png");

  await page.goto("/realtime");
  await expect(page.getByRole("heading", { name: "Realtime Analytics" })).toBeVisible();
  await shot(page, "07-realtime-analytics.png");
});
