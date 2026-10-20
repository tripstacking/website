"""List pre-screened Cosmic Themes and their Manifesto alignment."""

from __future__ import annotations

from tripstacking_website.themes import PRE_SCREENED_THEMES


def default() -> int:
    """List the 5 pre-screened Cosmic Themes, ports, and Manifesto alignment."""
    print("Pre-Screened Cosmic Themes for Trip Stacking:")
    print("-" * 78)
    for spec in PRE_SCREENED_THEMES:
        print(
            f"  {spec.name:<10} | http://127.0.0.1:{spec.port} | "
            f"Astro {spec.astro_version} | {spec.tagline}"
        )
        print(f"             | Folder: {spec.directory.relative_to(spec.directory.parents[1])}")
        print(f"             | Fit:    {spec.manifesto_fit}")
        print("-" * 78)
    return 0
