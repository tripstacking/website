import { defineConfig } from "astro/config";
import { unified } from "@astrojs/markdown-remark";
import tailwindcss from "@tailwindcss/vite";
import sitemap from "@astrojs/sitemap";
import mdx from "@astrojs/mdx";
import compress from "@playform/compress";
import icon from "astro-icon";
import react from "@astrojs/react";
import { appleMapsVitePlugin } from "../../shared/hero-map/appleMapsVitePlugin.mjs";

// https://astro.build/config
export default defineConfig({
  site: "https://tripstacking.com",
  output: "static",
  server: {
    host: "127.0.0.1",
    port: 4323,
  },
  i18n: {
    defaultLocale: "en",
    locales: ["en", "fr"],
    routing: {
      prefixDefaultLocale: false,
    },
  },
  markdown: {
    processor: unified(),
    shikiConfig: {
      theme: "dracula",
      wrap: true,
    },
  },
  integrations: [
    mdx(),
    react(),
    icon(),
    sitemap(),
    compress({
      HTML: true,
      JavaScript: true,
      CSS: false,
      Image: false,
      SVG: false,
    }),
  ],
  vite: {
    plugins: [tailwindcss(), appleMapsVitePlugin()],
    build: {
      assetsInlineLimit: 0,
    },
  },
});
