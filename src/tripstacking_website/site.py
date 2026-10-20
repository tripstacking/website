"""Configuration and process runner utilities for the Trip Stacking marketing site."""

from __future__ import annotations

import shutil
import subprocess
import webbrowser
from collections.abc import Callable
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SITE_DIR = REPO_ROOT / "site"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 4321

CommandRunner = Callable[[list[str], Path], int]
BrowserOpener = Callable[[str], object]


def resolve_pnpm_executable() -> str:
    """Resolve the pnpm executable on PATH."""
    found = shutil.which("pnpm")
    return found if found is not None else "pnpm"


def default_runner(command: list[str], cwd: Path) -> int:
    """Execute a subprocess command in the given working directory."""
    completed = subprocess.run(command, cwd=cwd, check=False)
    return int(completed.returncode)


def default_browser_opener(url: str) -> object:
    """Open a URL in a new browser tab."""
    return webbrowser.open_new_tab(url)
