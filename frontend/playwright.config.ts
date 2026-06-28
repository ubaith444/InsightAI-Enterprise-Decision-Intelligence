import { defineConfig, devices } from "@playwright/test";

const webServer = process.env.PLAYWRIGHT_SKIP_WEBSERVER
  ? undefined
  : [
      {
        command: "python -m uvicorn app.main:app --host 127.0.0.1 --port 8000",
        cwd: "../backend",
        url: "http://127.0.0.1:8000/health",
        reuseExistingServer: true,
        timeout: 30_000
      },
      {
        command: "npm run start",
        url: "http://127.0.0.1:3000",
        reuseExistingServer: true,
        timeout: 30_000
      }
    ];

export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  expect: { timeout: 10_000 },
  fullyParallel: false,
  reporter: [["list"], ["html", { outputFolder: "playwright-report", open: "never" }]],
  use: {
    baseURL: "http://127.0.0.1:3000",
    trace: "retain-on-failure",
    channel: "chrome"
  },
  webServer,
  projects: [
    {
      name: "chrome",
      use: { ...devices["Desktop Chrome"] }
    }
  ]
});
