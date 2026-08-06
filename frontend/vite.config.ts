import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

const BACKEND = 'http://127.0.0.1:8000'

// Everything under /api is proxied to the FastAPI backend, WebSocket included,
// so the app talks to same-origin paths in development and in production.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': { target: BACKEND, changeOrigin: true, ws: true },
    },
  },
  test: {
    // Component tests need a DOM; node is the default.
    environment: 'jsdom',
  },
})
