"""Process execution and browser launcher utilities for Astro theme commands."""

from __future__ import annotations

import os
import shutil
import signal
import subprocess
import time
import webbrowser
from collections.abc import Callable
from pathlib import Path

CommandRunner = Callable[[list[str], Path], int]
MultiCommandRunner = Callable[[list[tuple[str, list[str], Path]]], int]
BrowserOpener = Callable[[str], object]


def resolve_pnpm_executable() -> str:
    """Resolve the pnpm executable on PATH."""
    found = shutil.which("pnpm")
    return found if found is not None else "pnpm"


def default_runner(command: list[str], cwd: Path) -> int:
    """Execute a single subprocess command in the given working directory."""
    completed = subprocess.run(command, cwd=cwd, check=False)
    return int(completed.returncode)


def default_multi_runner(tasks: list[tuple[str, list[str], Path]]) -> int:
    """Launch multiple theme servers concurrently and wait until interrupted or exited."""
    processes: list[tuple[str, subprocess.Popen[bytes]]] = []
    try:
        for name, command, cwd in tasks:
            proc = subprocess.Popen(command, cwd=cwd, start_new_session=True)
            processes.append((name, proc))

        while processes:
            for name, proc in list(processes):
                ret = proc.poll()
                if ret is not None:
                    if ret != 0:
                        return int(ret)
                    processes.remove((name, proc))
            time.sleep(0.25)
        return 0
    except KeyboardInterrupt:
        return 0
    finally:
        for _, proc in processes:
            if proc.poll() is None:
                try:
                    os.killpg(proc.pid, signal.SIGTERM)
                except ProcessLookupError:
                    proc.terminate()
        for _, proc in processes:
            if proc.poll() is None:
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill()


def default_browser_opener(url: str) -> object:
    """Open a URL in a new browser tab."""
    return webbrowser.open_new_tab(url)
