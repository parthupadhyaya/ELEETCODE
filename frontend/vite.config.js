import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    strictPort: true,
    // The FastAPI backend (backend/main.py) runs on port 8000. Use 127.0.0.1,
    // not localhost: Node may resolve localhost to ::1, which uvicorn doesn't bind
    proxy: { '/api': 'http://127.0.0.1:8000' },
  },
})
