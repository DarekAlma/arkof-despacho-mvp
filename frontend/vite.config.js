import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// En desarrollo, las llamadas a /api y /confirmar se redirigen al backend Flask.
export default defineConfig({
  plugins: [react()],
  server: { port: 5173, proxy: { "/api": "http://localhost:5000", "/confirmar": "http://localhost:5000" } },
});
