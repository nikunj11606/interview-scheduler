import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    watch: {
      ignored: ['**/scheduler-backend/**']
    },
    proxy: {
      '/data': 'http://127.0.0.1:8000',
      '/chat': 'http://127.0.0.1:8000'
    },
    host: true,
    allowedHosts: [
      'localhost',
      '.ngrok-free.dev',
      '.ngrok.io'
    ]
  }
})