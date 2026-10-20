"""Top-level build command shortcut to build one or all Cosmic Themes."""

from __future__ import annotations

from tripstacking_website.commands.themes.build import default as themes_build


def default(
    theme: str = "all",
    dry_run: bool = False,
) -> int:
    """Build static Astro output for one or all pre-screened Cosmic Themes."""
    return themes_build(theme=theme, dry_run=dry_run)
