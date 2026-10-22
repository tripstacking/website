import cloudflare from "@astrojs/cloudflare";
import { unified } from "@astrojs/markdown-remark";
import mdx from "@astrojs/mdx";
import react from "@astrojs/react";
import sitemap from "@astrojs/sitemap";
import clerk from "@clerk/astro";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig, sessionDrivers } from "astro/config";
import icon from "astro-icon";

import { appleMapsVitePlugin } from "./src/components/hero-map/appleMapsVitePlugin.mjs";
import { getClerkAppearance } from "./src/js/clerkTheme.mjs";

// https://astro.build/config
export default defineConfig({
  site: "https://tripstacking.com",
  output: "server",
  adapter: cloudflare({
    imageService: "compile",
    prerenderEnvironment: "node",
  }),
  session: {
    driver: sessionDrivers.memory(),
  },
  server: {
    host: "127.0.0.1",
    port: 4321,
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
      wrap: false,
    },
  },
  integrations: [
    clerk({
      publishableKey:
        process.env.PUBLIC_CLERK_PUBLISHABLE_KEY ||
        "pk_test_ZnVubnktdnVsdHVyZS04MDE0LmNsZXJrLmFjY291bnRzLmRldiQ",
      signInUrl: "/login",
      signUpUrl: "/signup",
      waitlistUrl: "/waitlist",
      appearance: getClerkAppearance("light"),
    }),
    mdx(),
    react(),
    icon(),
    sitemap(),
  ],
  vite: {
    plugins: [tailwindcss(), appleMapsVitePlugin()],
    optimizeDeps: {
      include: [
        "@clerk/astro/client",
        "@clerk/astro/internal",
        "@clerk/astro/server",
        "astro-icon > @iconify/utils",
      ],
      exclude: [
        "@clerk/astro/components",
        "astro-icon/components",
        "astro-seo",
      ],
    },
    ssr: {
      optimizeDeps: {
        include: [
          "@clerk/astro/client",
          "@clerk/astro/internal",
          "@clerk/astro/server",
          "astro-icon > @iconify/utils",
        ],
        exclude: [
          "@clerk/astro/components",
          "astro-icon/components",
          "astro-seo",
        ],
      },
    },
    build: {
      target: "es2022",
    },
  },
});