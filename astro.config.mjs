// @ts-check
import { defineConfig } from 'astro/config';

import tailwindcss from '@tailwindcss/vite';

// https://astro.build/config
export default defineConfig({
  site: "https://karthik-s-salian.vercel.app",
  vite: {
    plugins: [tailwindcss()]
  }
});