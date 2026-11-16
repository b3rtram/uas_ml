// Vite: the development server. It turns our .jsx files into plain JavaScript for the browser.
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    // Section 5: every request to /api/... is passed on to the Session 5 backend (lecture05 01_monolith).
    // For the browser it looks like the same server, so no CORS problems.
    proxy: { "/api": "http://127.0.0.1:8000" },
  },
});
