import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: '../tests/e2e',
  fullyParallel: true,
  use: {
    baseURL: 'http://127.0.0.1:5417',
    launchOptions: process.env.MEDRESEARCH_BROWSER ? { executablePath: process.env.MEDRESEARCH_BROWSER } : {},
  },
  projects: [
    { name: 'desktop', use: { ...devices['Desktop Chrome'] } },
    { name: 'mobile', use: { ...devices['Pixel 7'] } },
  ],
  webServer: { command: 'node node_modules/vite/bin/vite.js --port 5417', url: 'http://127.0.0.1:5417', reuseExistingServer: false },
})
