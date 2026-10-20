"""Build static Cloudflare Worker bundles for one or all pre-screened Cosmic Themes."""

from __future__ import annotations

from typing import Annotated

from cyclopts import Parameter

from tripstacking_website.commands.themes._runner import (
    CommandRunner,
    default_runner,
    resolve_pnpm_executable,
)
from tripstacking_website.themes import resolve_selected_themes


def default(
    theme: str = "all",
    dry_run: bool = False,
    *,
    runner: Annotated[CommandRunner | None, Parameter(parse=False)] = None,
) -> int:
    """Build static Astro output (dist/) for one theme or all 5 themes."""
    selected = resolve_selected_themes(theme)
    pnpm = resolve_pnpm_executable()
    active_runner = runner if runner is not None else default_runner

    for spec in selected:
        cmd = [pnpm, "run", "build"]
        print(f"Building theme '{spec.name}' in {spec.directory} (dry_run={dry_run})...")
        if dry_run:
            continue
        exit_code = active_runner(cmd, spec.directory)
        if exit_code != 0:
            return exit_code
    return 0
