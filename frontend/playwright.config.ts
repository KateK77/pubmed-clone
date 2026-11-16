import { defineConfig, devices } from '@playwright/test'
import { mkdtempSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

process.env.MEDRESEARCH_TEST_STATE ??= mkdtempSync(join(tmpdir(), 'medresearch-e2e-'))
const python = process.env.MEDRESEARCH_TEST_PYTHON ?? 'python'

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
  webServer: [
    { command: '"' + python + '" ../tests/browser_server.py', url: 'http://127.0.0.1:8025/api/health/', reuseExistingServer: false },
    { command: 'node node_modules/vite/bin/vite.js --port 5417', url: 'http://127.0.0.1:5417',
      env: { MEDRESEARCH_API_TARGET: 'http://127.0.0.1:8025' }, reuseExistingServer: false },
  ],
})
