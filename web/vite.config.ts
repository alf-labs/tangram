import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  assetsInclude: ["**/*.md"],
  base: "",
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          libs: [
            "react",
            "react-bootstrap",
            "react-dom",
            "react-intersection-observer",
            "react-markdown",
            "react-router-dom",
            "react-virtualized-auto-sizer",
            "rehype-external-links",
            "rehype-raw",
            "remark-gfm",
          ],
        }
      }

    }
  }
})

