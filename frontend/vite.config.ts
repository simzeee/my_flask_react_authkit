import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://127.0.0.1:5000',
      '/login': 'http://127.0.0.1:5000',
      '/callback': 'http://127.0.0.1:5000',
      '/logout': 'http://127.0.0.1:5000',
      '/health': 'http://127.0.0.1:5000',
      '/dashboard': 'http://127.0.0.1:5000',
    }
  }
})
