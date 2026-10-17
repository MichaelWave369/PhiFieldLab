import { defineConfig } from 'vite';
export default defineConfig({
  base: '/PhiFieldLab/',
  esbuild: { jsx: 'automatic' },
  build: { outDir: 'dist', emptyOutDir: true }
});
