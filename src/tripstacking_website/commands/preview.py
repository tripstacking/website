"""Preview production build via Astro preview or Cloudflare Wrangler dev."""

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
    wrangler: bool = False,
    open_browser: Annotated[bool, Parameter(name=["--open", "--open-browser"])] = False,
    dry_run: bool = False,
    *,
    runner: Annotated[CommandRunner | None, Parameter(parse=False)] = None,
    browser_opener: Annotated[BrowserOpener | None, Parameter(parse=False)] = None,
) -> int:
    """Preview the static production build via Astro or Cloudflare Wrangler."""
    pnpm = resolve_pnpm_executable()
    url = f"http://{host}:{port}"
    if wrangler:
        cmd = [
            pnpm,
            "exec",
            "wrangler",
            "dev",
            "--ip",
            host,
            "--port",
            str(port),
        ]
    else:
        cmd = [
            pnpm,
            "exec",
            "astro",
            "preview",
            "--host",
            host,
            "--port",
            str(port),
            "--ignore-lock",
        ]
    mode = "wrangler" if wrangler else "astro preview"
    print(f"Previewing Trip Stacking marketing site ({mode}) at {url} (dry_run={dry_run})...")
    if dry_run:
        return 0

    if open_browser:
        opener = browser_opener if browser_opener is not None else default_browser_opener
        opener(url)

    active_runner = runner if runner is not None else default_runner
    return active_runner(cmd, SITE_DIR)
