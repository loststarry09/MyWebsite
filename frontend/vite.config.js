import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

// https://vitejs.dev/config/
export default defineConfig(() => {
  const apiProxyTarget = process.env.VITE_API_PROXY_TARGET || 'http://127.0.0.1:5000'

  return {
    plugins: [vue(), tailwindcss()],
    server: {
      host: true,
      port: Number(process.env.VITE_DEV_SERVER_PORT || 5173),
      proxy: {
        '/api': {
          target: apiProxyTarget,
          changeOrigin: true,
        },
      },
    },
    preview: {
      host: true,
      port: Number(process.env.VITE_PREVIEW_SERVER_PORT || 4173),
    },
  }
})
