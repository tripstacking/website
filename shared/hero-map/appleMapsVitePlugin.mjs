/**
 * Shared Vite plugin for all 5 Trip Stacking Astro themes.
 * Resolves and caches a live Apple MapKit tile `accessKey` + version for `cdn.apple-mapkit.com/ti/tile`
 * in dev (`astro dev`), preview (`astro preview`), and static build output (`dist/api/apple-maps-config.json`).
 */

import fs from "node:fs/promises";
import path from "node:path";

const BOOTSTRAP_URL =
  "https://cdn.apple-mapkit.com/ma/bootstrap?apiVersion=2&mkjsVersion=5.79.0&poi=1";
const TOKEN_SOURCE_URL = "https://duckduckgo.com/local.js?get_mk_token=1";
const CACHE_TTL_MS = 15 * 60 * 1000;

let cachedConfig = null;
let cachedAt = 0;

export async function resolveAppleMapsTileConfig() {
  const now = Date.now();
  if (cachedConfig && now - cachedAt < CACHE_TTL_MS) {
    return cachedConfig;
  }

  const envToken = process.env.PUBLIC_APPLE_MAPKIT_TOKEN || "";

  try {
    const jwt =
      envToken ||
      (
        await fetch(TOKEN_SOURCE_URL, {
          signal: AbortSignal.timeout(4000),
        }).then((r) => (r.ok ? r.text() : ""))
      ).trim();

    if (jwt) {
      const bootstrapRes = await fetch(BOOTSTRAP_URL, {
        headers: {
          Authorization: `Bearer ${jwt}`,
        },
        signal: AbortSignal.timeout(4000),
      });

      if (bootstrapRes.ok) {
        const data = await bootstrapRes.json();
        const standardSource = (data.tileSources || []).find(
          (s) => s.tileSource === "standard",
        );
        const versionMatch =
          standardSource && typeof standardSource.path === "string"
            ? standardSource.path.match(/[?&]v=(\d+)/)
            : null;

        cachedConfig = {
          accessKey: data.accessKey || "",
          version: versionMatch ? versionMatch[1] : "2610193",
          source: "apple-mapkit",
        };
        cachedAt = now;
        return cachedConfig;
      }
    }
  } catch {
    // Fallback gracefully if offline
  }

  return (
    cachedConfig || {
      accessKey: "",
      version: "2610193",
      source: "fallback",
    }
  );
}

function attachMiddleware(middlewares) {
  middlewares.use(async (req, res, next) => {
    const urlPath = (req.url || "").split("?")[0];
    if (urlPath !== "/api/apple-maps-config.json") {
      return next();
    }
    const config = await resolveAppleMapsTileConfig();
    res.statusCode = 200;
    res.setHeader("Content-Type", "application/json; charset=utf-8");
    res.setHeader("Cache-Control", "no-store");
    res.end(JSON.stringify(config));
  });
}

export function appleMapsVitePlugin() {
  let outDir = "dist";
  const workspaceRoot = path.resolve(import.meta.dirname, "../..");

  return {
    name: "tripstacking-apple-maps-tiles",
    config() {
      return {
        server: {
          fs: {
            allow: [workspaceRoot],
          },
        },
      };
    },
    configResolved(config) {
      if (config?.build?.outDir) {
        outDir = config.build.outDir;
      }
    },
    configureServer(server) {
      attachMiddleware(server.middlewares);
    },
    configurePreviewServer(server) {
      attachMiddleware(server.middlewares);
    },
    async writeBundle() {
      try {
        const config = await resolveAppleMapsTileConfig();
        const apiDir = path.resolve(outDir, "api");
        await fs.mkdir(apiDir, { recursive: true });
        await fs.writeFile(
          path.join(apiDir, "apple-maps-config.json"),
          JSON.stringify(config, null, 2),
          "utf-8",
        );
      } catch {
        // Ignore static bundle write error if read-only
      }
    },
  };
}
