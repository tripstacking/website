import { unified } from "@astrojs/markdown-remark";
import mdx from "@astrojs/mdx";
import react from "@astrojs/react";
import sitemap from "@astrojs/sitemap";
import compress from "@playform/compress";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "astro/config";
import icon from "astro-icon";
import { appleMapsVitePlugin } from "../../shared/hero-map/appleMapsVitePlugin.mjs";

// https://astro.build/config
export default defineConfig({
  site: "https://tripstacking.com",
  output: "static",
  server: {
    host: "127.0.0.1",
    port: 4324,
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
      theme: "css-variables",
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
      JavaScript: false,
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
