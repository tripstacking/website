# Trip Stacking Marketing Website (`website`)

Astro v7 static marketing site and Cosmic Themes evaluation workspace for **Trip Stacking** (`STACK YOUR STOPS. OWN YOUR WEEK.`), configured for zero-friction static deployment to **Cloudflare Workers** via **Wrangler** and **GitHub Actions**.

---

## Pre-Screened Cosmic Themes (`themes/`)

All 5 pre-screened themes run on **Astro 7.4.1** and **Tailwind CSS 4.3.2** with static output (`output: "static"`), `wrangler.jsonc` (`assets.directory = "./dist"`), and Trip Stacking's `60-30-10` brand tokens (`#44C0C5` Horizon Teal, `#77C57F` Flow Green, `#FFDE59` Beacon Yellow, `#1A2E35` Harbor Slate, `#F7FBF9` Alabaster Mint, `#0F1D22` Harbor Night):

| Theme | Folder | Default Port | Visual Personality & Manifesto Fit |
| :--- | :--- | :---: | :--- |
| **Nova** | `themes/nova` | `4321` | **Alternating Light & Dark SaaS**: Alternates Alabaster Mint (`#F7FBF9`) daylight sections and Harbor Night (`#0F1D22`) dark sections to mirror the 60-30-10 daylight calendar vs. CarPlay contrast. |
| **Zenith** | `themes/zenith` | `4322` | **Structured Data & Metric Cards**: High-trust Starwind UI cards and schedule dashboard showcase *Calm Over Complexity*, time-window constraints, and consolidated calendar blocks. |
| **Atlas** | `themes/atlas` | `4323` | **Approachable Consumer Workflow**: Warm rounded geometry and step-by-step visual flows fit everyday errand stacking, store-hour windows, and family schedule orchestration. |
| **Galaxy** | `themes/galaxy` | `4324` | **Harbor Night & CarPlay Glow**: High-contrast dark surfaces highlight the Harbor Slate (`#1A2E35`) squircle badge, S-curve route spine, and native iOS + CarPlay dashboard experience. |
| **Amplify** | `themes/amplify` | `4325` | **Interactive Multi-Stop Pipeline**: Glowing horizon arc and 4-step pipeline illustrate the flow from Places To-Do List to Multi-Day VRP Optimization and One-Tap Navigation. |

---

## Tooling & Setup (`asdf` + `uv` + `pnpm`)

Tool versions are pinned in `.tool-versions` (`nodejs 26.2.0`, `pre-commit 4.6.2`, `uv 0.13.3`) and `.python-version` (`3.15.0`).

```bash
# Install Node/JS dependencies across all 5 theme workspaces
pnpm install

# Sync Python CLI environment
uv sync
```

---

## Python CLI (`ts-website`)

Use the `ts-website` CLI (built with Cyclopts, matching `ts-assets` in the `assets` repository) to list, serve, build, and preview all 5 themes side-by-side in separate browser tabs:

```bash
# List all 5 pre-screened themes, ports, and Manifesto alignment
uv run ts-website themes list

# Launch all 5 themes simultaneously on ports 4321–4325 and open browser tabs
uv run ts-website serve --open

# Launch a single theme on its assigned port
uv run ts-website themes serve --theme nova --open

# Build static production bundles (dist/) for all 5 themes
uv run ts-website build

# Preview built static bundles with Cloudflare Wrangler locally
uv run ts-website themes preview --wrangler --open
```

---

## Cloudflare Workers Deployment (Wrangler + GitHub Actions)

Each theme directory contains a `wrangler.jsonc` configured for Cloudflare Workers Static Assets (`"assets": { "directory": "./dist" }`), and `.github/workflows/deploy.yml` automates deployment via `cloudflare/wrangler-action@v3`.
