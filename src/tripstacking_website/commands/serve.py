"""Serve the Trip Stacking Astro marketing site locally."""

from __future__ import annotations

from typing import Annotated

from cyclopts import Parameter

from tripstacking_website.site import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    SITE_DIR,
    BrowserOpener,
    CommandRunner,
    default_browser_opener,
    default_runner,
    resolve_pnpm_executable,
)


def default(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    open_browser: Annotated[bool, Parameter(name=["--open", "--open-browser"])] = False,
    dry_run: bool = False,
    *,
    runner: Annotated[CommandRunner | None, Parameter(parse=False)] = None,
    browser_opener: Annotated[BrowserOpener | None, Parameter(parse=False)] = None,
) -> int:
    """Launch the Astro development server for the marketing site."""
    pnpm = resolve_pnpm_executable()
    url = f"http://{host}:{port}"
    cmd = [
        pnpm,
        "exec",
        "astro",
        "dev",
        "--host",
        host,
        "--port",
        str(port),
    ]
    print(f"Serving Trip Stacking marketing site at {url} (dry_run={dry_run})...")
    if dry_run:
        return 0

    if open_browser:
        opener = browser_opener if browser_opener is not None else default_browser_opener
        opener(url)

    active_runner = runner if runner is not None else default_runner
    return active_runner(cmd, SITE_DIR)
