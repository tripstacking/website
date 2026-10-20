"""Registry and metadata for the pre-screened Cosmic Themes."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
THEMES_DIR = REPO_ROOT / "themes"


@dataclass(frozen=True)
class ThemeSpec:
    """Metadata and local server defaults for a pre-screened Cosmic Theme."""

    name: str
    display_name: str
    port: int
    astro_version: str
    tagline: str
    manifesto_fit: str

    @property
    def directory(self) -> Path:
        """Return the absolute path to the theme folder."""
        return THEMES_DIR / self.name


PRE_SCREENED_THEMES: tuple[ThemeSpec, ...] = (
    ThemeSpec(
        name="nova",
        display_name="Nova",
        port=4321,
        astro_version="7.4.1",
        tagline="Alternating Light & Dark SaaS",
        manifesto_fit=(
            "Alternating Alabaster Mint (#F7FBF9) daylight sections and Harbor Night (#0F1D22) "
            "dark sections mirror the 60-30-10 daylight calendar vs. CarPlay dashboard contrast."
        ),
    ),
    ThemeSpec(
        name="zenith",
        display_name="Zenith",
        port=4322,
        astro_version="7.4.1",
        tagline="Structured Data & Metric Cards",
        manifesto_fit=(
            "High-trust Starwind UI cards and clean schedule metrics showcase 'Calm Over Complexity', "
            "time-window constraints, and consolidated calendar blocks."
        ),
    ),
    ThemeSpec(
        name="atlas",
        display_name="Atlas",
        port=4323,
        astro_version="7.4.1",
        tagline="Approachable Consumer Workflow",
        manifesto_fit=(
            "Warm rounded geometry and step-by-step visual flows fit everyday errand stacking, "
            "store-hour windows, and family schedule orchestration."
        ),
    ),
    ThemeSpec(
        name="galaxy",
        display_name="Galaxy",
        port=4324,
        astro_version="7.4.1",
        tagline="Harbor Night & CarPlay Glow",
        manifesto_fit=(
            "Sleek high-contrast dark surfaces highlight the Harbor Slate (#1A2E35) squircle badge, "
            "S-curve route spine, and native iOS + CarPlay dashboard experience."
        ),
    ),
    ThemeSpec(
        name="amplify",
        display_name="Amplify",
        port=4325,
        astro_version="7.4.1",
        tagline="Interactive Multi-Stop Pipeline",
        manifesto_fit=(
            "Modern SaaS component grid and step timelines illustrate the 4 core pillars from "
            "Places To-Do List to Multi-Day VRP Optimization and One-Tap Navigation."
        ),
    ),
)

_THEME_BY_NAME: dict[str, ThemeSpec] = {spec.name: spec for spec in PRE_SCREENED_THEMES}


def get_theme_spec(name: str) -> ThemeSpec:
    """Lookup a pre-screened theme by name."""
    normalized = name.strip().lower()
    if normalized not in _THEME_BY_NAME:
        available = ", ".join(_THEME_BY_NAME)
        msg = f"Unknown theme '{name}'. Available themes: {available}"
        raise ValueError(msg)
    return _THEME_BY_NAME[normalized]


def resolve_selected_themes(theme: str = "all") -> tuple[ThemeSpec, ...]:
    """Return either all pre-screened themes or a single requested theme."""
    normalized = theme.strip().lower()
    if normalized == "all":
        return PRE_SCREENED_THEMES
    return (get_theme_spec(normalized),)
