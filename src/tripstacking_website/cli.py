"""Cyclopts CLI entrypoint for Trip Stacking website theme comparison and builds."""

from __future__ import annotations

from collections.abc import Sequence

from cyclopts import App

from tripstacking_website import __version__
from tripstacking_website.commands import register_commands

__all__ = ["app", "main"]

app = App(
    name="ts-website",
    help="Trip Stacking Astro marketing site theme launcher, comparison, and build CLI.",
    version=__version__,
)
register_commands(app)


def main(tokens: Sequence[str] | None = None) -> int:
    """Run the ts-website CLI application."""
    if tokens is not None:
        result = app(list(tokens), result_action="return_int_as_exit_code_else_zero")
        return int(result)
    result = app(result_action="return_int_as_exit_code_else_zero")
    return int(result)
