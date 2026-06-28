import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./demo",
  timeout: 300_000,
  expect: { timeout: 15_000 },
  reporter: [["list"]],
  use: {
    baseURL: "http://127.0.0.1:3000",
    channel: "chrome",
    trace: "off",
    video: "on",
    ...devices["Desktop Chrome"],
    viewport: { width: 1440, height: 960 }
  },
  webServer: [
    {
      command: "python -m uvicorn app.main:app --host 127.0.0.1 --port 8000",
      cwd: "../backend",
      url: "http://127.0.0.1:8000/health",
      reuseExistingServer: true,
      timeout: 30_000
    },
    {
      command: "npm.cmd run start",
      url: "http://127.0.0.1:3000",
      reuseExistingServer: true,
      timeout: 30_000
    }
  ],
  outputDir: "../docs/assets/demos/playwright-output"
});
