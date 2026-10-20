import { defineConfig } from "astro/config";
import tailwindcss from "@tailwindcss/vite";
import sitemap from "@astrojs/sitemap";
import mdx from "@astrojs/mdx";
import react from "@astrojs/react";
import icon from "astro-icon";
import { appleMapsVitePlugin } from "../../shared/hero-map/appleMapsVitePlugin.mjs";

// https://astro.build/config
export default defineConfig({
  site: "https://tripstacking.com",
  output: "static",
  server: {
    host: "127.0.0.1",
    port: 4322,
  },
  i18n: {
    defaultLocale: "en",
    locales: ["en", "fr"],
    routing: {
      prefixDefaultLocale: false,
    },
  },
  markdown: {
    shikiConfig: {
      theme: "css-variables",
      wrap: true,
    },
  },
  integrations: [
    mdx(),
    react(),
    icon(),
    sitemap(),
  ],
  vite: {
    plugins: [tailwindcss(), appleMapsVitePlugin()],
    build: {
      assetsInlineLimit: 0,
      target: "es2022",
    },
  },
});
