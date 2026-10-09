import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [tailwindcss(), sveltekit()],
  // In dev - forward API calls (HTTP and WebSocket) to FastAPI
  // In production the backend serves the built UI, so /api is already same-origin.
  server: {
    proxy: {
      '/api': { target: 'http://127.0.0.1:8000', ws: true }
    }
  }
});
