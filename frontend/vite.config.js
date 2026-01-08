import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const baseUrl = "http://localhost:9000";
console.log("Using backend URL:", baseUrl);
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    outDir: "../static",
    emptyOutDir: true,
  },
  server: {
    proxy: {
      "/libraries": {
        target: baseUrl,
        changeOrigin: true,
      },
      "/convert": {
        target: baseUrl,
        changeOrigin: true,
      },
      "/compare": {
        target: baseUrl,
        changeOrigin: true,
      },
      "/history": {
        target: baseUrl,
        changeOrigin: true,
      },
      "/stats": {
        target: baseUrl,
        changeOrigin: true,
      },
      "/health": {
        target: baseUrl,
        changeOrigin: true,
      },
    },
  },
});
