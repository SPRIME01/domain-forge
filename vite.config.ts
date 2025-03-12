import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "path";
import { configDefaults } from "vitest/config";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": resolve(__dirname, "./domainforge"),
    },
  },
  server: {
    port: 3000,
    // BEGIN SECURITY CHECKS
    hmr: {
      protocol: "ws",
      host: "localhost",
    },
    // END SECURITY CHECKS
  },
  build: {
    outDir: "build",
    sourcemap: true,
    // BEGIN PERFORMANCE OPTIMIZATION
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ["react", "react-dom"],
        },
      },
    },
    // END PERFORMANCE OPTIMIZATION
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./domainforge/frontend/test/setup.ts"],
    include: ["**/*.{test,spec}.{ts,tsx}"],
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      exclude: ["node_modules/", "test/setup.ts"],
    },
  },
});
