import { expect, test } from "@playwright/test";

const unique = () => Math.random().toString(16).slice(2, 10);

test("complete InsightAI AI journey renders chart and persists artifacts", async ({ page }) => {
  const suffix = unique();
  await page.goto("/register");
  await page.getByPlaceholder("Full name").fill(`E2E Analyst ${suffix}`);
  await page.getByPlaceholder("Email").fill(`e2e-${suffix}@example.com`);
  await page.getByPlaceholder("Password").fill("InsightAI123");
  await page.getByRole("button", { name: "Create account" }).click();

  await expect(page.getByRole("heading", { name: "Dashboard Home" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Admin" })).toHaveCount(0);

  await page.goto("/connections");
  await expect(page.getByText("Loading workspace")).toHaveCount(0);
  await page.getByPlaceholder("Warehouse name").fill("E2E PostgreSQL Demo");
  await page.getByPlaceholder("Database URI").fill("sqlite:///./insightai.db");
  await page.getByPlaceholder("Selected tables or collections").fill("sales, customers, products");
  await page.getByRole("button", { name: "Add database" }).click();
  await expect(page.getByText("Connection created and audit logged.")).toBeVisible();
  await expect(page.getByText("sqlite:///./insightai.db")).toHaveCount(0);
  await expect(page.getByText("sqlite://***")).toBeVisible();

  await page.goto("/schema");
  await expect(page.getByRole("heading", { name: "sales" })).toBeVisible();
  await expect(page.getByText("revenue")).toBeVisible();

  await page.goto("/chat");
  await page.getByRole("textbox").fill("Show monthly revenue trend for the last 12 months");
  await page.getByRole("button", { name: "Generate and run" }).click();
  await expect(page.getByText("Query validated and executed.")).toBeVisible();
  await expect(page.getByTestId("query-chart")).toBeVisible();
  await expect(page.getByText("InsightAI analyzed")).toBeVisible();
  await page.getByRole("button", { name: "Save to dashboard" }).click();
  await expect(page.getByText("Saved to dashboard.")).toBeVisible();

  await page.goto("/dashboards");
  await expect(page.getByText("Saved: Show monthly revenue trend")).toBeVisible();

  await page.goto("/reports");
  await expect(page.getByText("Loading workspace")).toHaveCount(0);
  await page.getByRole("button", { name: "Generate" }).click();
  await expect(page.getByText("Report generated and audit logged.")).toBeVisible();
  await page.getByRole("button", { name: "PDF" }).first().click();
  await expect(page.getByText("PDF export downloaded.")).toBeVisible();

  await page.goto("/history");
  await expect(page.getByText("Show monthly revenue trend for the last 12 months")).toBeVisible();

  await page.goto("/admin");
  await expect(page.getByText("Admin access required")).toBeVisible();
});

test("mock AI asks for clarification on vague prompt in UI", async ({ page }) => {
  const suffix = unique();
  await page.goto("/register");
  await page.getByPlaceholder("Full name").fill(`E2E Clarify ${suffix}`);
  await page.getByPlaceholder("Email").fill(`clarify-${suffix}@example.com`);
  await page.getByPlaceholder("Password").fill("InsightAI123");
  await page.getByRole("button", { name: "Create account" }).click();
  await expect(page.getByRole("heading", { name: "Dashboard Home" })).toBeVisible();

  await page.goto("/chat");
  await page.getByRole("textbox").fill("show something");
  await page.getByRole("button", { name: "Generate and run" }).click();
  await expect(page.getByText("Please clarify the metric").first()).toBeVisible();
});
