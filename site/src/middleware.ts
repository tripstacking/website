import { clerkMiddleware } from "@clerk/astro/server";
import type { MiddlewareHandler } from "astro";

const DEFAULT_PUBLISHABLE_KEY =
  "pk_test_ZnVubnktdnVsdHVyZS04MDE0LmNsZXJrLmFjY291bnRzLmRldiQ";

export const onRequest: MiddlewareHandler = async (context, next) => {
  if (context.url.pathname.startsWith("/api/")) {
    return next();
  }

  let cfEnv: Record<string, unknown> | undefined;
  try {
    const cf = await import(/* @vite-ignore */ "cloudflare:workers");
    cfEnv = cf?.env as Record<string, unknown> | undefined;
  } catch {
    // Non-Cloudflare runtime
  }

  const secretKey =
    (typeof cfEnv?.CLERK_SECRET_KEY === "string" && cfEnv.CLERK_SECRET_KEY) ||
    (typeof process !== "undefined" && process.env?.CLERK_SECRET_KEY) ||
    import.meta.env.CLERK_SECRET_KEY ||
    "";

  const publishableKey =
    (typeof cfEnv?.PUBLIC_CLERK_PUBLISHABLE_KEY === "string" &&
      cfEnv.PUBLIC_CLERK_PUBLISHABLE_KEY) ||
    (typeof process !== "undefined" &&
      process.env?.PUBLIC_CLERK_PUBLISHABLE_KEY) ||
    import.meta.env.PUBLIC_CLERK_PUBLISHABLE_KEY ||
    DEFAULT_PUBLISHABLE_KEY;

  if (!secretKey || !publishableKey) {
    return next();
  }

  try {
    const handler = clerkMiddleware({ publishableKey, secretKey });
    return await handler(context, next);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    if (
      message.includes("Missing Clerk Secret Key") ||
      message.includes("Publishable key is missing") ||
      message.includes("Missing publishableKey")
    ) {
      return next();
    }
    throw err;
  }
};
