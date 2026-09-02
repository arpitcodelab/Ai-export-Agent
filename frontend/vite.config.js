import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// The React dev server can run on port 5173 by default.
// It proxies /api to the FastAPI backend so the frontend never needs to
// hardcode the backend URL.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
