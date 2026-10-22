import type { APIRoute } from "astro";

import { resolveAppleMapsTileConfig } from "../../components/hero-map/appleMapsVitePlugin.mjs";

export const prerender = false;

export const GET: APIRoute = async ({ url }) => {
  const fromNodeMiddleware = url.searchParams.get("node") === "1";
  const config = await resolveAppleMapsTileConfig({ fromNodeMiddleware });
  return new Response(JSON.stringify(config), {
    status: 200,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
    },
  });
};
