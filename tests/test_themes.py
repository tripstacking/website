"""Tests for pre-screened Cosmic Themes registry and directory structure."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tripstacking_website.themes import (
    PRE_SCREENED_THEMES,
    THEMES_DIR,
    ThemeSpec,
    get_theme_spec,
    resolve_selected_themes,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_THEME_NAMES = ("nova", "zenith", "atlas", "galaxy", "amplify")


def test_at_least_five_pre_screened_themes_registered() -> None:
    assert len(PRE_SCREENED_THEMES) >= 5
    names = tuple(spec.name for spec in PRE_SCREENED_THEMES)
    assert names == EXPECTED_THEME_NAMES


def test_theme_ports_are_unique_and_sequential() -> None:
    ports = [spec.port for spec in PRE_SCREENED_THEMES]
    assert len(set(ports)) == len(ports)
    assert ports == [4321, 4322, 4323, 4324, 4325]


def test_get_theme_spec_and_resolve_selected_themes() -> None:
    nova = get_theme_spec("nova")
    assert isinstance(nova, ThemeSpec)
    assert nova.name == "nova"
    assert nova.port == 4321
    assert nova.directory == THEMES_DIR / "nova"

    single = resolve_selected_themes("zenith")
    assert len(single) == 1
    assert single[0].name == "zenith"

    all_themes = resolve_selected_themes("all")
    assert len(all_themes) == 5

    with pytest.raises(ValueError, match="Unknown theme"):
        get_theme_spec("nonexistent")


@pytest.mark.parametrize("theme_name", EXPECTED_THEME_NAMES)
def test_theme_folder_exists_with_astro_and_wrangler_config(theme_name: str) -> None:
    spec = get_theme_spec(theme_name)
    assert spec.directory.is_dir(), f"Missing theme directory {spec.directory}"

    pkg_path = spec.directory / "package.json"
    assert pkg_path.is_file()
    pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
    assert "astro" in deps

    wrangler_path = spec.directory / "wrangler.jsonc"
    assert wrangler_path.is_file(), f"Missing wrangler.jsonc in {spec.directory}"
    wrangler_text = wrangler_path.read_text(encoding="utf-8")
    assert "./dist" in wrangler_text


@pytest.mark.parametrize("theme_name", EXPECTED_THEME_NAMES)
def test_theme_branding_and_manifesto_home_page(theme_name: str) -> None:
    spec = get_theme_spec(theme_name)

    tailwind_theme = (spec.directory / "src" / "styles" / "tailwind-theme.css").read_text(
        encoding="utf-8"
    )
    for hex_token in ("#44C0C5", "#77C57F", "#FFDE59", "#1A2E35", "#F7FBF9"):
        assert hex_token.lower() in tailwind_theme.lower(), (
            f"{theme_name} tailwind-theme.css missing brand token {hex_token}"
        )

    site_data = (spec.directory / "src" / "config" / "en" / "siteData.json.ts").read_text(
        encoding="utf-8"
    )
    assert "Trip Stacking" in site_data
    assert "STACK YOUR STOPS. OWN YOUR WEEK." in site_data

    index_page = (spec.directory / "src" / "pages" / "index.astro").read_text(encoding="utf-8")
    for required_copy in (
        "STACK YOUR STOPS. OWN YOUR WEEK.",
        "Constraint-Aware",
        "Multi-Day",
        "Calendar",
        "CarPlay",
        "#44C0C5",
        "#77C57F",
        "#FFDE59",
    ):
        assert required_copy in index_page, (
            f"{theme_name} src/pages/index.astro missing '{required_copy}'"
        )


def test_shared_hero_map_component_exists_once() -> None:
    shared_dir = REPO_ROOT / "shared" / "hero-map"
    component_path = shared_dir / "HeroMapBackground.astro"
    core_path = shared_dir / "heroMapCore.mjs"
    plugin_path = shared_dir / "appleMapsVitePlugin.mjs"

    assert component_path.is_file(), "Shared HeroMapBackground.astro must exist in shared/hero-map/"
    assert core_path.is_file(), "Shared heroMapCore.mjs must exist in shared/hero-map/"
    assert plugin_path.is_file(), "Shared appleMapsVitePlugin.mjs must exist in shared/hero-map/"

    core_text = core_path.read_text(encoding="utf-8")
    assert "45.5152" in core_text and "-122.6784" in core_text, (
        "Default Portland, OR coordinates must be defined in heroMapCore.mjs"
    )
    assert "cdn.apple-mapkit.com/ti/tile" in core_text
    for brand_hex in ("#44C0C5", "#77C57F", "#FFDE59", "#1A2E35", "#F7FBF9"):
        assert brand_hex.lower() in core_text.lower()

    component_text = component_path.read_text(encoding="utf-8")
    assert "blur(" in component_text, "Expected optical blur on map tiles for accessibility contrast"
    assert "data-map-scrim" in component_text, "Expected high-contrast scrim layer over map background"
    assert "data-return-home-paths" in component_text, (
        "Expected distinct return-to-home route path group in HeroMapBackground.astro"
    )
    assert component_text.index("data-map-svg") < component_text.index("data-map-scrim"), (
        "Contrast scrim must sit above both tiles and route SVG so foreground marketing text is easy to read"
    )


def test_shared_hero_map_core_random_stops_and_tiles_with_node() -> None:
    import subprocess

    core_path = REPO_ROOT / "shared" / "hero-map" / "heroMapCore.mjs"
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


@pytest.mark.parametrize("theme_name", EXPECTED_THEME_NAMES)
def test_all_themes_use_shared_hero_map_background(theme_name: str) -> None:
    spec = get_theme_spec(theme_name)
    index_page = (spec.directory / "src" / "pages" / "index.astro").read_text(encoding="utf-8")
    assert "HeroMapBackground" in index_page, (
        f"{theme_name} index.astro must use the shared HeroMapBackground component"
    )
    assert "shared/hero-map/HeroMapBackground.astro" in index_page

    astro_config = (spec.directory / "astro.config.mjs").read_text(encoding="utf-8")
    assert "appleMapsVitePlugin" in astro_config, (
        f"{theme_name} astro.config.mjs must register shared appleMapsVitePlugin"
    )


