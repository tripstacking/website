"""Serve one or all pre-screened Cosmic Themes locally for side-by-side comparison."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from cyclopts import Parameter

from tripstacking_website.commands.themes._runner import (
    BrowserOpener,
    CommandRunner,
    MultiCommandRunner,
    default_browser_opener,
    default_multi_runner,
    default_runner,
    resolve_pnpm_executable,
)
from tripstacking_website.themes import resolve_selected_themes


def default(
    theme: str = "all",
    host: str = "127.0.0.1",
    port: int | None = None,
    open_browser: Annotated[bool, Parameter(name=["--open", "--open-browser"])] = False,
    dry_run: bool = False,
    *,
    runner: Annotated[CommandRunner | None, Parameter(parse=False)] = None,
    multi_runner: Annotated[MultiCommandRunner | None, Parameter(parse=False)] = None,
    browser_opener: Annotated[BrowserOpener | None, Parameter(parse=False)] = None,
) -> int:
    """Launch Astro dev servers for a specific theme or all 5 themes on distinct ports."""
    selected = resolve_selected_themes(theme)
    pnpm = resolve_pnpm_executable()
    opener = browser_opener if browser_opener is not None else default_browser_opener

    tasks: list[tuple[str, list[str], Path]] = []
    urls: list[str] = []

    for spec in selected:
        active_port = port if (port is not None and len(selected) == 1) else spec.port
        url = f"http://{host}:{active_port}"
        urls.append(url)
        cmd = [
            pnpm,
            "exec",
            "astro",
            "dev",
            "--host",
            host,
            "--port",
            str(active_port),
        ]
        tasks.append((spec.name, cmd, spec.directory))
        print(f"Serving theme '{spec.name}' ({spec.tagline}) at {url} (dry_run={dry_run})...")

    if dry_run:
        return 0

    if open_browser:
        for url in urls:
            opener(url)

    if len(tasks) == 1:
        active_runner = runner if runner is not None else default_runner
        _, single_cmd, single_cwd = tasks[0]
        return active_runner(single_cmd, single_cwd)

    active_multi = multi_runner if multi_runner is not None else default_multi_runner
    return active_multi(tasks)
