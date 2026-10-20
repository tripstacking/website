"""Build static Cloudflare Worker bundle for the Trip Stacking marketing site."""

from __future__ import annotations

from typing import Annotated

from cyclopts import Parameter

from tripstacking_website.site import (
    SITE_DIR,
    CommandRunner,
    default_runner,
    resolve_pnpm_executable,
)


def default(
    dry_run: bool = False,
    *,
    runner: Annotated[CommandRunner | None, Parameter(parse=False)] = None,
) -> int:
    """Build static Astro output (dist/) for the marketing site."""
    pnpm = resolve_pnpm_executable()
    cmd = [pnpm, "run", "build"]
    print(f"Building Trip Stacking marketing site in {SITE_DIR} (dry_run={dry_run})...")
    if dry_run:
        return 0

    active_runner = runner if runner is not None else default_runner
    return active_runner(cmd, SITE_DIR)
