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


def test_clerk_and_cloudflare_workers_configuration() -> None:
    pkg = json.loads((SITE_DIR / "package.json").read_text(encoding="utf-8"))
    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
    assert "@clerk/astro" in deps
    assert "@astrojs/cloudflare" in deps

    astro_config = (SITE_DIR / "astro.config.mjs").read_text(encoding="utf-8")
    assert "@clerk/astro" in astro_config
    assert "@astrojs/cloudflare" in astro_config
    assert 'output: "server"' in astro_config or "output: 'server'" in astro_config
    assert "adapter: cloudflare(" in astro_config
    assert "clerk(" in astro_config

    wrangler_text = (SITE_DIR / "wrangler.jsonc").read_text(encoding="utf-8")
    assert "nodejs_compat" in wrangler_text
    assert "@astrojs/cloudflare/entrypoints/server" in wrangler_text

    middleware_text = (SITE_DIR / "src" / "middleware.ts").read_text(encoding="utf-8")
    assert "clerkMiddleware" in middleware_text

    for auth_page in (
        SITE_DIR / "src" / "pages" / "sign-in.astro",
        SITE_DIR / "src" / "pages" / "sign-up.astro",
        SITE_DIR / "src" / "pages" / "fr" / "sign-in.astro",
        SITE_DIR / "src" / "pages" / "fr" / "sign-up.astro",
    ):
        assert auth_page.is_file(), f"Missing Clerk auth page {auth_page}"

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
        '<span class="block whitespace-nowrap">STACK YOUR STOPS.</span>',
        '<span class="block whitespace-nowrap">OWN YOUR WEEK.</span>',
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


def test_language_selector_disabled_while_i18n_support_preserved() -> None:
    site_settings = (SITE_DIR / "src" / "config" / "siteSettings.json.ts").read_text(
        encoding="utf-8"
    )
    assert 'export const locales = ["en", "fr"]' in site_settings

    nav = (SITE_DIR / "src" / "components" / "Nav" / "Nav.astro").read_text(encoding="utf-8")
    assert "LanguageSelect" not in nav
    assert 'href="/#pricing"' in nav

    mobile_nav = (
        SITE_DIR / "src" / "components" / "Nav" / "MobileNav" / "MobileNav.astro"
    ).read_text(encoding="utf-8")
    assert "MobileLanguageSelect" not in mobile_nav
    assert 'href="/#pricing"' in mobile_nav


def test_index_replaces_reviews_with_four_column_subscription_pricing() -> None:
    index_page = (SITE_DIR / "src" / "pages" / "index.astro").read_text(encoding="utf-8")
    assert "PricingFourCards" in index_page
    assert "TestimonialsRows" not in index_page

    pricing_component = (
        SITE_DIR / "src" / "components" / "Pricing" / "PricingFourCards.astro"
    ).read_text(encoding="utf-8")
    for required_tier in (
        "Free",
        "Local Pro",
        "Cloud Sync",
        "Family & Household",
        "2.99",
        "19.99",
        "3.99",
        "29.99",
        "6.99",
        "49.99",
    ):
        assert required_tier in pricing_component, (
            f"PricingFourCards.astro missing '{required_tier}'"
        )

    lowered = pricing_component.lower()
    assert "lifetime" not in lowered
    assert "one-time" not in lowered
    assert "24.99" not in lowered
    assert "phase 1" not in lowered
    assert "per household" not in lowered
    assert "free forever" not in lowered
    assert "vrp" not in lowered
    assert "testing" not in lowered
    assert "Everything in Free" in pricing_component
    assert "In-app route map & Apple CarPlay" in pricing_component
    assert "Shared Family Stacker (Up to 5)" in pricing_component
    assert "Smart Multi-Driver Trip Splitting" in pricing_component
    assert '<span class="pricing-monthly">per month</span>' in pricing_component
    assert '<span class="pricing-yearly hidden">per year</span>' in pricing_component
    assert "pricing-yearly hidden" in pricing_component
    assert "comingSoon: true" in pricing_component
    assert "roadmapNote" not in pricing_component
    assert 'linkText: "Coming Soon"' in pricing_component
    assert "disabled" in pricing_component


def test_pricing_available_tiers_are_waitlist_login() -> None:
    pricing_component = (
        SITE_DIR / "src" / "components" / "Pricing" / "PricingFourCards.astro"
    ).read_text(encoding="utf-8")
    assert "waitlist: true" in pricing_component
    assert 'linkText: "Join Waitlist"' in pricing_component
    assert "/waitlist?tier=free" in pricing_component
    assert "/waitlist?tier=local-pro" in pricing_component
    assert "Start Stacking Free" not in pricing_component
    assert "Subscribe to Local Pro" not in pricing_component
    assert 'when="signed-in"' in pricing_component
    assert 'when="signed-out"' in pricing_component
    assert "On the Waitlist" in pricing_component


def test_waitlist_page_renders_clerk_waitlist_with_site_palette() -> None:
    waitlist_page = SITE_DIR / "src" / "pages" / "waitlist.astro"
    fr_waitlist_page = SITE_DIR / "src" / "pages" / "fr" / "waitlist.astro"
    waitlist_form = SITE_DIR / "src" / "components" / "Forms" / "WaitlistForm.astro"

    assert waitlist_page.is_file(), "waitlist.astro must exist in site/src/pages/"
    assert fr_waitlist_page.is_file(), "waitlist.astro must exist in site/src/pages/fr/"
    assert waitlist_form.is_file(), "WaitlistForm.astro must exist in site/src/components/Forms/"

    form_text = waitlist_form.read_text(encoding="utf-8")
    assert "Waitlist" in form_text
    assert "@clerk/astro/components" in form_text
    assert "getClerkAppearance" in form_text
    assert "syncClerkAppearanceWithTheme" in form_text
    assert "astro:page-load" in form_text

    clerk_theme = (SITE_DIR / "src" / "js" / "clerkTheme.mjs").read_text(encoding="utf-8")
    assert '"waitlist"' in clerk_theme
    assert '"mountWaitlist"' in clerk_theme

    clerk_theme_path = SITE_DIR / "src" / "js" / "clerkTheme.mjs"
    node_script = (
        f"import({json.dumps(clerk_theme_path.as_uri())}).then((m) => {{"
        "  const waitlistLight = m.getClerkAppearance('light', { hideHeader: false });"
        "  const waitlistDark = m.getClerkAppearance('dark', { hideHeader: false });"
        "  console.log(JSON.stringify({ waitlistLight, waitlistDark }));"
        "});"
    )
    res = subprocess.run(
        ["node", "-e", node_script],
        capture_output=True,
        text=True,
        check=True,
    )
    waitlist_payload = json.loads(res.stdout.strip())
    for key in ("waitlistLight", "waitlistDark"):
        elements = waitlist_payload[key]["elements"]
        assert elements.get("header", {}).get("display") != "none"
        assert elements["headerTitle"].get("display") != "none"
        assert elements["headerSubtitle"].get("display") != "none"

    global_css = (SITE_DIR / "src" / "styles" / "global.css").read_text(encoding="utf-8")
    assert ":has(form) .cl-header" in global_css

    astro_config = (SITE_DIR / "astro.config.mjs").read_text(encoding="utf-8")
    assert 'waitlistUrl: "/waitlist"' in astro_config


def test_waitlist_page_persists_status_in_local_storage_and_shows_already_on_list() -> None:
    storage_helper = SITE_DIR / "src" / "js" / "waitlistStorage.mjs"
    assert storage_helper.is_file(), "waitlistStorage.mjs must exist in site/src/js/"

    node_script = (
        f"import({json.dumps(storage_helper.as_uri())}).then((m) => {{"
        "  const store = new Map();"
        "  const mockStorage = {"
        "    getItem: (k) => (store.has(k) ? store.get(k) : null),"
        "    setItem: (k, v) => store.set(k, v),"
        "    removeItem: (k) => store.delete(k),"
        "  };"
        "  const before = m.readWaitlistStatus(mockStorage);"
        "  const saved = m.saveWaitlistStatus({ email: 'traveler@example.com', tier: 'local-pro' }, mockStorage);"
        "  const after = m.readWaitlistStatus(mockStorage);"
        "  m.clearWaitlistStatus(mockStorage);"
        "  const cleared = m.readWaitlistStatus(mockStorage);"
        "  console.log(JSON.stringify({ before, saved, after, cleared }));"
        "});"
    )
    res = subprocess.run(
        ["node", "-e", node_script],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(res.stdout.strip())
    assert payload["before"] is None
    assert payload["saved"]["joined"] is True
    assert payload["saved"]["email"] == "traveler@example.com"
    assert payload["saved"]["tier"] == "free"
    assert payload["after"]["joined"] is True
    assert payload["after"]["email"] == "traveler@example.com"
    assert payload["after"]["tier"] == "free"
    assert payload["cleared"] is None

    waitlist_form = (SITE_DIR / "src" / "components" / "Forms" / "WaitlistForm.astro").read_text(
        encoding="utf-8"
    )
    assert "waitlistStorage.mjs" in waitlist_form
    assert "readWaitlistStatus" in waitlist_form
    assert "saveWaitlistStatus" in waitlist_form
    assert "data-waitlist-already-joined" in waitlist_form
    assert "On the Waitlist • Free" in waitlist_form
    assert "On the Waitlist • Local Pro" not in waitlist_form
    assert "for this browser" not in waitlist_form
    assert "Your spot on the Trip Stacking Free tier waitlist is confirmed." in waitlist_form


def test_nav_and_auth_pages_render_clerk_and_waitlist_avatar() -> None:
    nav = (SITE_DIR / "src" / "components" / "Nav" / "Nav.astro").read_text(encoding="utf-8")
    assert "@clerk/astro/components" in nav
    assert 'when="signed-in"' in nav
    assert "UserWaitlistAvatar" in nav
    assert '"/login"' not in nav

    mobile_nav = (
        SITE_DIR / "src" / "components" / "Nav" / "MobileNav" / "MobileNav.astro"
    ).read_text(encoding="utf-8")
    assert "@clerk/astro/components" in mobile_nav
    assert 'when="signed-in"' in mobile_nav
    assert "UserWaitlistAvatar" in mobile_nav
    assert '"/login"' not in mobile_nav

    assert (SITE_DIR / "src" / "pages" / "login.astro").is_file()
    assert 'ThemeToggle class="my-auto mr-3 -ml-4 hidden md:block"' in nav

    login_form = (SITE_DIR / "src" / "components" / "Forms" / "LoginForm.astro").read_text(
        encoding="utf-8"
    )
    assert "SignIn" in login_form
    assert "UserWaitlistAvatar" in login_form
    assert "Waitlist Sign In" not in login_form
    assert "Sign In" in login_form

    signup_form = (SITE_DIR / "src" / "components" / "Forms" / "SignupForm.astro").read_text(
        encoding="utf-8"
    )
    assert "SignUp" in signup_form
    assert "UserWaitlistAvatar" in signup_form
    assert "Waitlist" in signup_form


def test_clerk_and_waitlist_colors_match_site_palette_in_light_and_dark_modes() -> None:
    clerk_theme_path = SITE_DIR / "src" / "js" / "clerkTheme.mjs"
    assert clerk_theme_path.is_file(), "clerkTheme.mjs must exist in site/src/js/"

    node_script = (
        f"import({json.dumps(clerk_theme_path.as_uri())}).then((m) => {{"
        "  const light = m.getClerkAppearance('light');"
        "  const dark = m.getClerkAppearance('dark');"
        "  globalThis.document = { documentElement: { classList: { contains: () => false } } };"
        "  globalThis.localStorage = { getItem: (k) => (k === 'colorTheme' ? 'dark' : null) };"
        "  const detectedFromStorage = m.detectCurrentThemeMode();"
        "  console.log(JSON.stringify({ light, dark, detectedFromStorage }));"
        "});"
    )
    res = subprocess.run(
        ["node", "-e", node_script],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(res.stdout.strip())
    assert payload["detectedFromStorage"] == "dark"
    light_vars = payload["light"]["variables"]
    dark_vars = payload["dark"]["variables"]

    # Light mode uses Trip Stacking primary & base light palette tokens
    assert light_vars["colorPrimary"].upper() in ("#1F8388", "#1D696E")
    assert light_vars["colorPrimaryForeground"].upper() == "#F7FBF9"
    assert light_vars["colorForeground"].upper() == "#1A2E35"
    assert light_vars["colorBackground"].upper() in ("#FFFFFF", "#F7FBF9")
    assert light_vars["colorInput"].upper() == "#F7FBF9"
    assert light_vars["colorBorder"].upper() == "#B5CCC5"

    # Dark mode uses Trip Stacking dark brand palette tokens
    assert dark_vars["colorPrimary"].upper() in ("#44C0C5", "#2BA3A8")
    assert dark_vars["colorBackground"].upper() == "#1A2E35"
    assert dark_vars["colorForeground"].upper() == "#F7FBF9"
    assert dark_vars["colorInput"].upper() == "#0F1D22"
    assert dark_vars["colorBorder"].upper() == "#243E47"

    # Both light and dark appearances hide Clerk's built-in card header/title/subtitle
    for mode_key in ("light", "dark"):
        elements = payload[mode_key]["elements"]
        assert elements["header"]["display"] == "none"
        assert elements["headerTitle"]["display"] == "none"
        assert elements["headerSubtitle"]["display"] == "none"

    # Waitlist avatar component supports both light and dark modes with site palette
    avatar_comp = (
        SITE_DIR / "src" / "components" / "Profile" / "UserWaitlistAvatar.astro"
    ).read_text(encoding="utf-8")
    assert "dark:" in avatar_comp
    assert "bg-primary-50" in avatar_comp or "bg-base-100" in avatar_comp

    # Login and Signup forms apply getClerkAppearance and sync with dark/light mode toggle
    login_form = (SITE_DIR / "src" / "components" / "Forms" / "LoginForm.astro").read_text(
        encoding="utf-8"
    )
    signup_form = (SITE_DIR / "src" / "components" / "Forms" / "SignupForm.astro").read_text(
        encoding="utf-8"
    )
    assert "getClerkAppearance" in login_form
    assert "getClerkAppearance" in signup_form
    assert "astro:page-load" in login_form
    assert "astro:page-load" in signup_form

    # Global CSS removes legacy fuchsia/pure-black overrides in favor of Trip Stacking tokens
    global_css = (SITE_DIR / "src" / "styles" / "global.css").read_text(encoding="utf-8")
    assert "fuchsia" not in global_css
    assert "--card: var(--color-base-900)" in global_css


def test_all_pages_use_trip_stacking_title_prefix_and_nav_login_changes_to_logout() -> None:
    title_utils_path = SITE_DIR / "src" / "js" / "titleUtils.mjs"
    assert title_utils_path.is_file(), "titleUtils.mjs must exist in site/src/js/"

    node_script = (
        f"import({json.dumps(title_utils_path.as_uri())}).then((m) => {{"
        "  const out = {"
        "    login: m.formatPageTitle('Login'),"
        "    alreadyPrefixed: m.formatPageTitle('Trip Stacking - Login'),"
        "    emDash: m.formatPageTitle('Trip Stacking — STACK YOUR STOPS. OWN YOUR WEEK.'),"
        "    about: m.formatPageTitle('About Us'),"
        "  };"
        "  console.log(JSON.stringify(out));"
        "});"
    )
    res = subprocess.run(
        ["node", "-e", node_script],
        capture_output=True,
        text=True,
        check=True,
    )
    formatted = json.loads(res.stdout.strip())
    assert formatted["login"] == "Trip Stacking - Login"
    assert formatted["alreadyPrefixed"] == "Trip Stacking - Login"
    assert formatted["emDash"] == "Trip Stacking - STACK YOUR STOPS. OWN YOUR WEEK."
    assert formatted["about"] == "Trip Stacking - About Us"

    seo_astro = (SITE_DIR / "src" / "components" / "Seo" / "Seo.astro").read_text(encoding="utf-8")
    assert "formatPageTitle" in seo_astro

    nav_astro = (SITE_DIR / "src" / "components" / "Nav" / "Nav.astro").read_text(encoding="utf-8")
    assert 'when="signed-in"' in nav_astro
    assert '"/login"' not in nav_astro
    assert "Logout" in nav_astro
    assert "SignOutButton" in nav_astro

    mobile_nav = (
        SITE_DIR / "src" / "components" / "Nav" / "MobileNav" / "MobileNav.astro"
    ).read_text(encoding="utf-8")
    assert '"/login"' not in mobile_nav
    assert "Logout" in mobile_nav
    assert "SignOutButton" in mobile_nav


def test_site_uses_in_app_routing_and_carplay_without_external_maps_export() -> None:
    files_to_check = (
        SITE_DIR / "src" / "pages" / "index.astro",
        SITE_DIR / "src" / "components" / "Pricing" / "PricingFourCards.astro",
        SITE_DIR / "src" / "config" / "en" / "faqData.json.ts",
        SITE_DIR / "src" / "config" / "en" / "siteData.json.ts",
    )
    for file_path in files_to_check:
        text = file_path.read_text(encoding="utf-8")
        lowered = text.lower()
        assert "google maps" not in lowered, f"{file_path.name} must not mention Google Maps export"
        assert "apple maps" not in lowered, f"{file_path.name} must not mention Apple Maps export"
        assert "carplay" in lowered, f"{file_path.name} must mention CarPlay"


def test_site_favicon_is_tripstacking_svg_with_light_dark_theme_css() -> None:
    base_head = (SITE_DIR / "src" / "layouts" / "BaseHead.astro").read_text(encoding="utf-8")
    assert 'href="/brand/favicon.svg"' in base_head
    assert 'type="image/svg+xml"' in base_head
    assert 'href="/brand/apple-touch-icon.png"' in base_head
    assert 'name="color-scheme" content="light dark"' in base_head
    assert "#603cba" not in base_head.lower()

    favicon_svg = (SITE_DIR / "public" / "brand" / "favicon.svg").read_text(encoding="utf-8")
    assert "<style>" in favicon_svg
    assert "prefers-color-scheme: dark" in favicon_svg
    for hex_color in ("#FFDE59", "#77C57F", "#44C0C5", "#1A2E35", "#F7FBF9"):
        assert hex_color.lower() in favicon_svg.lower()


def test_index_orders_how_it_works_before_feature_highlights_with_marketing_copy() -> None:
    index_page = (SITE_DIR / "src" / "pages" / "index.astro").read_text(encoding="utf-8")
    how_it_works_pos = index_page.index('id="how-it-works"')
    features_pos = index_page.index('id="features"')
    assert how_it_works_pos < features_pos, (
        "From Scattered Errands to One Smooth S-Curve (#how-it-works) must come before #features"
    )
    assert "From Scattered Errands to One Smooth S-Curve" in index_page
    assert "Feature Highlights" in index_page

    lowered = index_page.lower()
    for design_jargon in (
        "60-30-10 visual system",
        "nova theme",
        "valhalla + vroom",
        "pillar 01",
        "four pillars",
    ):
        assert design_jargon not in lowered, (
            f"Design/internal copy '{design_jargon}' should be removed from index.astro"
        )

    nav_data = (SITE_DIR / "src" / "config" / "en" / "navData.json.ts").read_text(encoding="utf-8")
    assert "Calendar & CarPlay" not in nav_data
    assert "/#carplay" not in nav_data
    for link in ("/#how-it-works", "/#features", "/#pricing", "/#faq"):
        assert link in nav_data


def test_footer_contains_only_copyright_without_upper_links_or_socials() -> None:
    footer = (SITE_DIR / "src" / "components" / "Footer" / "Footer.astro").read_text(
        encoding="utf-8"
    )
    assert "All rights reserved." in footer
    for removed in (
        "FooterLink",
        "SocialIcon",
        "Landing Pages",
        "Sections",
        "Forms",
        "twitter.com",
    ):
        assert removed not in footer, f"Footer.astro must not include '{removed}'"


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

    api_endpoint = SITE_DIR / "src" / "pages" / "api" / "apple-maps-config.json.ts"
    assert api_endpoint.is_file(), (
        "apple-maps-config.json.ts SSR endpoint must exist in site/src/pages/api/"
    )


def test_apple_maps_workerd_user_agent_and_fallback_tile_upgrade_with_node() -> None:
    core_path = SITE_DIR / "src" / "components" / "hero-map" / "heroMapCore.mjs"
    plugin_path = SITE_DIR / "src" / "components" / "hero-map" / "appleMapsVitePlugin.mjs"
    script = f"""
import {{
  buildAppleMapsTileUrl,
  buildFallbackTileUrl,
  shouldReuseLoadedTile,
  resolveTileImageSrc,
}} from {json.dumps(core_path.as_uri())};
import {{
  resolveAppleMapsTileConfig,
}} from {json.dumps(plugin_path.as_uri())};

// 1. Simulate Cloudflare workerd fetch where missing User-Agent returns empty token body
const seenUserAgents = [];
const mockWorkerdFetch = async (url, init = {{}}) => {{
  const headers = new Headers(init.headers || {{}});
  const ua = headers.get("user-agent") || "";
  seenUserAgents.push(ua);
  if (String(url).includes("duckduckgo.com")) {{
    if (!ua) {{
      return new Response("", {{ status: 200 }});
    }}
    return new Response("mock_jwt_token", {{ status: 200 }});
  }}
  if (String(url).includes("cdn.apple-mapkit.com/ma/bootstrap")) {{
    return new Response(
      JSON.stringify({{
        accessKey: "live_apple_access_key",
        tileSources: [{{ tileSource: "standard", path: "/ti/tile?v=2610204" }}],
      }}),
      {{ status: 200, headers: {{ "content-type": "application/json" }} }},
    );
  }}
  throw new Error("Unexpected URL: " + url);
}};

const config = await resolveAppleMapsTileConfig({{
  forceRefresh: true,
  fetchImpl: mockWorkerdFetch,
}});
if (config.accessKey !== "live_apple_access_key" || config.version !== "2610204") {{
  throw new Error("Expected workerd fetch with User-Agent to resolve live accessKey, got: " + JSON.stringify(config));
}}
if (seenUserAgents.some((ua) => !ua)) {{
  throw new Error("Expected all upstream fetches to include a non-empty User-Agent header");
}}

// 1b. Simulate Miniflare workerd 403 on bootstrap (CF-Worker: *.example.com) falling back to local Node middleware
const mockMiniflare403Fetch = async (url) => {{
  const u = String(url);
  if (u.includes("duckduckgo.com")) {{
    return new Response("mock_jwt_token", {{ status: 200 }});
  }}
  if (u.includes("cdn.apple-mapkit.com/ma/bootstrap")) {{
    return new Response("403 Forbidden", {{ status: 403 }});
  }}
  if (u.includes("127.0.0.1:4321/api/apple-maps-config.json?node=1")) {{
    return new Response(
      JSON.stringify({{
        accessKey: "node_middleware_access_key",
        version: "2610204",
        source: "apple-mapkit",
      }}),
      {{ status: 200, headers: {{ "content-type": "application/json" }} }},
    );
  }}
  throw new Error("Unexpected URL: " + u);
}};

const fallbackFrom403Config = await resolveAppleMapsTileConfig({{
  forceRefresh: true,
  fetchImpl: mockMiniflare403Fetch,
}});
if (fallbackFrom403Config.accessKey !== "node_middleware_access_key") {{
  throw new Error("Expected 403 in Miniflare workerd to fall back to local Node middleware config");
}}

// 2. SSR fallback tile must upgrade to Apple Maps primaryUrl once accessKey is available
const fallbackUrl = buildFallbackTileUrl({{ x: 649, y: 1463, z: 12, dark: true }});
const primaryUrl = buildAppleMapsTileUrl({{
  x: 649,
  y: 1463,
  z: 12,
  accessKey: "live_apple_access_key",
  version: "2610204",
  dark: true,
}});

// Even if the SSR fallback image finished loading, shouldReuseLoadedTile must return false when primaryUrl differs
if (
  shouldReuseLoadedTile({{
    currentSrc: fallbackUrl,
    primaryUrl,
    complete: true,
    naturalWidth: 512,
    failedPrimarySrc: "",
  }}) !== false
) {{
  throw new Error("SSR fallback tile must not short-circuit upgrade to Apple Maps primaryUrl");
}}

// Once upgraded to primaryUrl and loaded, shouldReuseLoadedTile returns true
if (
  shouldReuseLoadedTile({{
    currentSrc: primaryUrl,
    primaryUrl,
    complete: true,
    naturalWidth: 512,
    failedPrimarySrc: "",
  }}) !== true
) {{
  throw new Error("Loaded Apple Maps primary tile should be reused");
}}

// resolveTileImageSrc upgrades fallbackUrl -> primaryUrl unless primaryUrl already failed
const upgradedSrc = resolveTileImageSrc({{
  currentSrc: fallbackUrl,
  primaryUrl,
  fallbackUrl,
  failedPrimarySrc: "",
}});
if (upgradedSrc !== primaryUrl) {{
  throw new Error("Expected fallbackUrl to upgrade to primaryUrl, got: " + upgradedSrc);
}}

// If primaryUrl specifically failed to load, keep fallbackUrl
const afterErrorSrc = resolveTileImageSrc({{
  currentSrc: fallbackUrl,
  primaryUrl,
  fallbackUrl,
  failedPrimarySrc: primaryUrl,
}});
if (afterErrorSrc !== fallbackUrl) {{
  throw new Error("Expected failed primaryUrl to stay on fallbackUrl, got: " + afterErrorSrc);
}}
"""
    proc = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, f"Node test failed: {proc.stderr}"


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


def test_user_avatar_resolves_social_login_or_gravatar_for_email_only() -> None:
    avatar_path = SITE_DIR / "src" / "js" / "avatarUtils.mjs"
    assert avatar_path.is_file(), "avatarUtils.mjs must exist in site/src/js/"

    script = f"""
import {{
  md5Hex,
  computeGravatarUrl,
  resolveUserAvatar,
}} from {json.dumps(avatar_path.as_uri())};

// Known MD5 vector for 'user@example.com'
const hash = md5Hex("user@example.com");
if (hash !== "b58996c504c5638798eb6b511e6f49af") {{
  throw new Error("Unexpected MD5 for user@example.com: " + hash);
}}

const gravatarUrl = computeGravatarUrl("  User@Example.com ");
if (!gravatarUrl.startsWith("https://www.gravatar.com/avatar/b58996c504c5638798eb6b511e6f49af")) {{
  throw new Error("Unexpected Gravatar URL: " + gravatarUrl);
}}

// 1. Social login user -> uses social provider avatar
const socialUser = {{
  firstName: "Alex",
  fullName: "Alex Rivera",
  hasImage: true,
  imageUrl: "https://img.clerk.com/oauth_google_avatar",
  primaryEmailAddress: {{ emailAddress: "alex@example.com" }},
  externalAccounts: [
    {{
      provider: "oauth_google",
      imageUrl: "https://lh3.googleusercontent.com/a/alex-social-avatar",
    }},
  ],
}};
const socialResult = resolveUserAvatar(socialUser);
if (socialResult.source !== "social" || socialResult.url !== "https://lh3.googleusercontent.com/a/alex-social-avatar") {{
  throw new Error("Expected social avatar URL, got: " + JSON.stringify(socialResult));
}}

// 2. Email-only user (no externalAccounts, hasImage=false) -> uses Gravatar
const emailOnlyUser = {{
  firstName: "Taylor",
  hasImage: false,
  imageUrl: "https://img.clerk.com/default_placeholder",
  primaryEmailAddress: {{ emailAddress: "  User@Example.com " }},
  externalAccounts: [],
}};
const emailResult = resolveUserAvatar(emailOnlyUser);
if (
  emailResult.source !== "gravatar" ||
  !emailResult.url.startsWith("https://www.gravatar.com/avatar/b58996c504c5638798eb6b511e6f49af")
) {{
  throw new Error("Expected Gravatar URL for email-only user, got: " + JSON.stringify(emailResult));
}}
"""
    proc = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, f"Avatar Node test failed: {proc.stderr}"
