"""Tests for the Trip Stacking Astro marketing site (Nova theme) in `site/`."""

from __future__ import annotations

import json
import subprocess

from tripstacking_website.site import DEFAULT_HOST, DEFAULT_PORT, REPO_ROOT, SITE_DIR


def test_site_constants_and_single_theme_structure() -> None:
    assert SITE_DIR == REPO_ROOT / "site"
    assert SITE_DIR.is_dir(), f"Missing site directory {SITE_DIR}"
    assert not (REPO_ROOT / "themes").exists(), "Legacy themes/ directory must be removed"
    assert not (REPO_ROOT / "shared").exists(), "Legacy shared/ directory must be moved into site/"
    assert DEFAULT_HOST == "127.0.0.1"
    assert DEFAULT_PORT == 4321


def test_site_has_astro_and_wrangler_config() -> None:
    pkg_path = SITE_DIR / "package.json"
    assert pkg_path.is_file()
    pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
    assert "astro" in deps

    wrangler_path = SITE_DIR / "wrangler.jsonc"
    assert wrangler_path.is_file(), f"Missing wrangler.jsonc in {SITE_DIR}"
    wrangler_text = wrangler_path.read_text(encoding="utf-8")
    assert "./dist" in wrangler_text

    workflow_path = REPO_ROOT / ".github" / "workflows" / "deploy.yml"
    workflow_text = workflow_path.read_text(encoding="utf-8")
    assert "working-directory: site" in workflow_text
    assert "workingDirectory: site" in workflow_text
    for removed in ("zenith", "atlas", "galaxy", "amplify"):
        assert removed not in workflow_text.lower()


def test_site_branding_and_manifesto_home_page() -> None:
    tailwind_theme = (SITE_DIR / "src" / "styles" / "tailwind-theme.css").read_text(
        encoding="utf-8"
    )
    for hex_token in ("#44C0C5", "#77C57F", "#FFDE59", "#1A2E35", "#F7FBF9"):
        assert hex_token.lower() in tailwind_theme.lower(), (
            f"site tailwind-theme.css missing brand token {hex_token}"
        )

    site_data = (SITE_DIR / "src" / "config" / "en" / "siteData.json.ts").read_text(
        encoding="utf-8"
    )
    assert "Trip Stacking" in site_data
    assert "STACK YOUR STOPS. OWN YOUR WEEK." in site_data

    index_page = (SITE_DIR / "src" / "pages" / "index.astro").read_text(encoding="utf-8")
    for required_copy in (
        "STACK YOUR STOPS.<br />\n            OWN YOUR WEEK.",
        "Constraint-Aware",
        "Multi-Day",
        "Calendar",
        "CarPlay",
        "#44C0C5",
        "#77C57F",
        "#FFDE59",
    ):
        assert required_copy in index_page, f"site/src/pages/index.astro missing '{required_copy}'"


def test_site_uses_single_sans_web_font_without_sentient_serif() -> None:
    base_head = (SITE_DIR / "src" / "layouts" / "BaseHead.astro").read_text(encoding="utf-8")
    assert "InterVariable" in base_head
    assert "sentient" not in base_head.lower()
    assert "fontshare" not in base_head.lower()

    tailwind_theme = (SITE_DIR / "src" / "styles" / "tailwind-theme.css").read_text(
        encoding="utf-8"
    )
    assert '"InterVariable"' in tailwind_theme
    assert "sentient" not in tailwind_theme.lower()
    assert "--font-serif" not in tailwind_theme

    global_css = (SITE_DIR / "src" / "styles" / "global.css").read_text(encoding="utf-8")
    assert "font-serif" not in global_css

    index_page = (SITE_DIR / "src" / "pages" / "index.astro").read_text(encoding="utf-8")
    assert "font-serif" not in index_page


def test_hero_map_component_in_site() -> None:
    hero_map_dir = SITE_DIR / "src" / "components" / "hero-map"
    component_path = hero_map_dir / "HeroMapBackground.astro"
    core_path = hero_map_dir / "heroMapCore.mjs"
    plugin_path = hero_map_dir / "appleMapsVitePlugin.mjs"

    assert component_path.is_file(), (
        "HeroMapBackground.astro must exist in site/src/components/hero-map/"
    )
    assert core_path.is_file(), "heroMapCore.mjs must exist in site/src/components/hero-map/"
    assert plugin_path.is_file(), (
        "appleMapsVitePlugin.mjs must exist in site/src/components/hero-map/"
    )

    core_text = core_path.read_text(encoding="utf-8")
    assert "45.5152" in core_text and "-122.6784" in core_text, (
        "Default Portland, OR coordinates must be defined in heroMapCore.mjs"
    )
    assert "cdn.apple-mapkit.com/ti/tile" in core_text
    for brand_hex in ("#44C0C5", "#77C57F", "#FFDE59", "#1A2E35", "#F7FBF9"):
        assert brand_hex.lower() in core_text.lower()

    component_text = component_path.read_text(encoding="utf-8")
    assert "blur(" in component_text, (
        "Expected optical blur on map tiles for accessibility contrast"
    )
    assert "data-map-scrim" in component_text, (
        "Expected high-contrast scrim layer over map background"
    )
    assert "data-return-home-paths" in component_text, (
        "Expected distinct return-to-home route path group in HeroMapBackground.astro"
    )
    assert component_text.index("data-map-svg") < component_text.index("data-map-scrim"), (
        "Contrast scrim must sit above both tiles and route SVG so foreground marketing text is easy to read"
    )

    index_page = (SITE_DIR / "src" / "pages" / "index.astro").read_text(encoding="utf-8")
    assert "HeroMapBackground" in index_page
    assert "@components/hero-map/HeroMapBackground.astro" in index_page

    astro_config = (SITE_DIR / "astro.config.mjs").read_text(encoding="utf-8")
    assert "appleMapsVitePlugin" in astro_config


def test_hero_map_core_random_stops_and_tiles_with_node() -> None:
    core_path = SITE_DIR / "src" / "components" / "hero-map" / "heroMapCore.mjs"
    script = f"""
import {{
  DEFAULT_LOCATION,
  DEFAULT_ZOOM,
  MIN_STOPS,
  MAX_STOPS,
  computeViewportTiles,
  buildAppleMapsTileUrl,
  generateRandomRouteForBounds,
}} from {json.dumps(core_path.as_uri())};

if (DEFAULT_LOCATION.lat !== 45.5152 || DEFAULT_LOCATION.lng !== -122.6784) {{
  throw new Error("Expected Portland OR default location");
}}
if (MIN_STOPS !== 3 || MAX_STOPS !== 8) {{
  throw new Error("Expected 3-8 stops range");
}}
const tiles = computeViewportTiles(DEFAULT_LOCATION.lat, DEFAULT_LOCATION.lng, DEFAULT_ZOOM, 1440, 800);
if (!Array.isArray(tiles) || tiles.length < 6) {{
  throw new Error("Expected viewport tile coverage");
}}
const url = buildAppleMapsTileUrl({{ x: tiles[0].x, y: tiles[0].y, z: DEFAULT_ZOOM, accessKey: "test_key", dark: true }});
if (!url.includes("cdn.apple-mapkit.com/ti/tile") || !url.includes("tint=dark")) {{
  throw new Error("Unexpected Apple Maps tile URL: " + url);
}}
const seenCounts = new Set();
for (let i = 0; i < 40; i++) {{
  const route = generateRandomRouteForBounds(1440, 800);
  if (route.stops.length < 3 || route.stops.length > 8) {{
    throw new Error("Stop count out of [3, 8]: " + route.stops.length);
  }}
  seenCounts.add(route.stops.length);
  for (const s of route.stops) {{
    if (s.x < 0 || s.x > 1440 || s.y < 0 || s.y > 800) {{
      throw new Error("Stop outside screen bounds");
    }}
  }}
  if (!route.svgPath.startsWith("M ")) {{
    throw new Error("Expected valid SVG path");
  }}
  if (!route.returnToHome || !route.returnHomeSvgPath.startsWith("M ")) {{
    throw new Error("Expected configurable returnToHome path by default");
  }}
}}
const openRoute = generateRandomRouteForBounds(1440, 800, Math.random, {{ returnToHome: false }});
if (openRoute.returnToHome !== false || openRoute.returnHomeSvgPath !== "") {{
  throw new Error("Expected returnHomeSvgPath to be empty when returnToHome is false");
}}
if (seenCounts.size < 3) {{
  throw new Error("Expected random variation in stop counts between 3 and 8");
}}
"""
    proc = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, f"Node test failed: {proc.stderr}"
