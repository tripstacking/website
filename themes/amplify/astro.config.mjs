import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

import mdx from "@astrojs/mdx";
import react from "@astrojs/react";
import sitemap from "@astrojs/sitemap";
import compress from "@playform/compress";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "astro/config";
import icon from "astro-icon";
import { appleMapsVitePlugin } from "../../shared/hero-map/appleMapsVitePlugin.mjs";

const astroCacheDir = path.join(os.tmpdir(), "amplify-astro-cache");
const viteCacheDir = path.join(os.tmpdir(), "amplify-vite-cache");
const picomatchShim = fileURLToPath(new URL("./src/shims/picomatch.mjs", import.meta.url));

// https://astro.build/config
export default defineConfig({
  site: "https://tripstacking.com",
  output: "static",
  server: {
    host: "127.0.0.1",
    port: 4325,
  },
  cacheDir: astroCacheDir,
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
      wrap: false,
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
    cacheDir: viteCacheDir,
    plugins: [tailwindcss(), appleMapsVitePlugin()],
    resolve: {
      alias: {
        picomatch: picomatchShim,
      },
    },
  },
});
