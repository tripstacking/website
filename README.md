# Trip Stacking Marketing Website (`website`)

Astro v7 static marketing site for **Trip Stacking** (`STACK YOUR STOPS. OWN YOUR WEEK.`), built on the **Nova** theme with **Astro 7.4.1** and **Tailwind CSS 4.3.2**, configured for static deployment to **Cloudflare Workers** via **Wrangler** and **GitHub Actions**.

---

## Site Architecture (`site/`)

The marketing site in `site/` runs on **Astro 7.4.1** and **Tailwind CSS 4.3.2** with static output (`output: "static"`), `wrangler.jsonc` (`assets.directory = "./dist"`), and Trip Stacking's `60-30-10` brand tokens (`#44C0C5` Horizon Teal, `#77C57F` Flow Green, `#FFDE59` Beacon Yellow, `#1A2E35` Harbor Slate, `#F7FBF9` Alabaster Mint, `#0F1D22` Harbor Night):

- **Alternating Light & Dark SaaS (`Nova`)**: Alternates Alabaster Mint (`#F7FBF9`) daylight sections and Harbor Night (`#0F1D22`) dark sections to mirror the 60-30-10 daylight calendar vs. CarPlay dashboard contrast.
- **Interactive Apple Maps Hero (`site/src/components/hero-map/`)**: Renders live Apple Maps dark raster tiles with a randomized 3–8 stop low-stress S-curve route and return-to-home arc.

---

## Tooling & Setup (`asdf` + `uv` + `pnpm`)

Tool versions are pinned in `.tool-versions` (`nodejs 26.2.0`, `pre-commit 4.6.2`, `uv 0.13.3`) and `.python-version` (`3.15.0`).

```bash
# Install Node/JS dependencies
pnpm install

# Sync Python CLI environment
uv sync
```

---

## Python CLI (`ts-website`)

Use the `ts-website` CLI (built with Cyclopts) to serve, build, and preview the marketing site:

```bash
# Launch the local Astro development server on http://127.0.0.1:4321
uv run ts-website serve --open

# Build the static production bundle (site/dist/)
uv run ts-website build

# Preview the built static bundle with Cloudflare Wrangler locally
uv run ts-website preview --wrangler --open
```

---

## Cloudflare Workers Deployment (Wrangler + GitHub Actions)

`site/wrangler.jsonc` is configured for Cloudflare Workers Static Assets (`"assets": { "directory": "./dist" }`), and `.github/workflows/deploy.yml` automates deployment via `cloudflare/wrangler-action@v3`.
