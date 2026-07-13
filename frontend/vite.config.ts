import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// Build output goes into the Python package so `kqm ui` can serve it with no
// Node at runtime (shipped as package data). Dev proxies /api to the local
// FastAPI server started via `kqm ui --mock`.
export default defineConfig({
  plugins: [react(), tailwindcss()],
  build: {
    outDir: "../src/kqm/webui",
    emptyOutDir: true,
  },
  server: {
    port: 5173,
    proxy: {
      "/api": "http://127.0.0.1:8420",
    },
  },
});
