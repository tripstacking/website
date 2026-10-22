/**
 * Vite plugin for the Trip Stacking Astro marketing site.
 * Resolves and caches a live Apple MapKit tile `accessKey` + version for `cdn.apple-mapkit.com/ti/tile`
 * in dev (`astro dev`), preview (`astro preview`), and static build output (`dist/api/apple-maps-config.json`).
 */

import fs from "node:fs/promises";
import path from "node:path";

const BOOTSTRAP_URL =
  "https://cdn.apple-mapkit.com/ma/bootstrap?apiVersion=2&mkjsVersion=5.79.0&poi=1";
const TOKEN_SOURCE_URL = "https://duckduckgo.com/local.js?get_mk_token=1";
const DEFAULT_USER_AGENT =
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15";
const CACHE_TTL_MS = 15 * 60 * 1000;

let cachedConfig = null;
let cachedAt = 0;

export async function resolveAppleMapsTileConfig(options = {}) {
  const { forceRefresh = false, fetchImpl = globalThis.fetch } = options ?? {};
  const now = Date.now();
  if (
    !forceRefresh &&
    cachedConfig &&
    cachedConfig.accessKey &&
    now - cachedAt < CACHE_TTL_MS
  ) {
    return cachedConfig;
  }

  try {
    const envToken =
      globalThis.process?.env?.PUBLIC_APPLE_MAPKIT_TOKEN || "";
    const jwt =
      envToken ||
      (
        await fetchImpl(TOKEN_SOURCE_URL, {
          headers: {
            "User-Agent": DEFAULT_USER_AGENT,
            Accept: "*/*",
            Referer: "https://duckduckgo.com/",
          },
          signal: AbortSignal.timeout(4000),
        }).then((r) => (r.ok ? r.text() : ""))
      ).trim();

    if (jwt) {
      const bootstrapRes = await fetchImpl(BOOTSTRAP_URL, {
        headers: {
          Authorization: `Bearer ${jwt}`,
          "User-Agent": DEFAULT_USER_AGENT,
          Accept: "application/json",
          Origin: "https://duckduckgo.com",
          Referer: "https://duckduckgo.com/",
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

        if (data.accessKey) {
          cachedConfig = {
            accessKey: data.accessKey,
            version: versionMatch ? versionMatch[1] : "2610193",
            source: "apple-mapkit",
          };
          cachedAt = now;
          return cachedConfig;
        }
      } else if (bootstrapRes.status === 403 && !options?.fromNodeMiddleware) {
        // Local Miniflare/workerd injects `CF-Worker: <name>.example.com`, which Apple CDN 403s.
        // Fall back to the local Vite Node middleware endpoint which fetches outside workerd.
        const localRes = await fetchImpl(
          "http://127.0.0.1:4321/api/apple-maps-config.json?node=1",
          { signal: AbortSignal.timeout(3000) },
        );
        if (localRes.ok) {
          const localData = await localRes.json();
          if (localData && localData.accessKey) {
            cachedConfig = localData;
            cachedAt = now;
            return cachedConfig;
          }
        }
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
    const config = await resolveAppleMapsTileConfig({
      fromNodeMiddleware: true,
    });
    res.statusCode = 200;
    res.setHeader("Content-Type", "application/json; charset=utf-8");
    res.setHeader("Cache-Control", "no-store");
    res.end(JSON.stringify(config));
  });
}

export function appleMapsVitePlugin() {
  let outDir = "dist";
  const workspaceRoot = path.resolve(import.meta.dirname, "../../..");

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
