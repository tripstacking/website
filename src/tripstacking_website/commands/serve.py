"""Top-level serve command shortcut to launch one or all Cosmic Themes."""

from __future__ import annotations

from typing import Annotated

from cyclopts import Parameter

from tripstacking_website.commands.themes.serve import default as themes_serve


def default(
    theme: str = "all",
    host: str = "127.0.0.1",
    port: int | None = None,
    open_browser: Annotated[bool, Parameter(name=["--open", "--open-browser"])] = False,
    dry_run: bool = False,
) -> int:
    """Serve one or all pre-screened Cosmic Themes locally on distinct ports."""
    return themes_serve(
        theme=theme,
        host=host,
        port=port,
        open_browser=open_browser,
        dry_run=dry_run,
    )
