import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: '127.0.0.1',
    port: 5184,
    strictPort: true,
    proxy: { '/api': { target: process.env.MEDRESEARCH_API_TARGET ?? 'http://127.0.0.1:8014' } },
  },
  test: { environment: 'jsdom', include: ['src/**/*.test.tsx'] },
})
