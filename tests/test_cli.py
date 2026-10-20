"""Unit tests for the Trip Stacking website CLI (`ts-website`)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from tripstacking_website import __version__
from tripstacking_website.cli import app, main


def test_cli_version(capsys: pytest.CaptureFixture[str]) -> None:
    app(["--version"], result_action="return_value")
    captured = capsys.readouterr()
    assert __version__ in captured.out


def test_cli_help(capsys: pytest.CaptureFixture[str]) -> None:
    app(["--help"], result_action="return_value")
    captured = capsys.readouterr()
    assert "ts-website" in captured.out
    assert "serve" in captured.out
    assert "build" in captured.out
    assert "preview" in captured.out
    assert "themes" not in captured.out


def test_serve_dry_run(capsys: pytest.CaptureFixture[str]) -> None:
    result = app(
        ["serve", "--host", "127.0.0.1", "--port", "4321", "--dry-run"],
        result_action="return_value",
    )
    captured = capsys.readouterr()
    assert "127.0.0.1:4321" in captured.out
    assert result == 0


def test_serve_invokes_runner_and_browser_opener() -> None:
    from tripstacking_website.commands.serve import default as serve_cmd

    recorded: list[tuple[list[str], Path]] = []
    opened_urls: list[str] = []

    def fake_runner(cmd: list[str], cwd: Path) -> int:
        recorded.append((cmd, cwd))
        return 0

    exit_code = serve_cmd(
        host="127.0.0.1",
        port=4321,
        open_browser=True,
        runner=fake_runner,
        browser_opener=opened_urls.append,
    )
    assert exit_code == 0
    assert len(recorded) == 1
    cmd, cwd = recorded[0]
    assert "astro" in cmd
    assert "dev" in cmd
    assert cwd.name == "site"
    assert opened_urls == ["http://127.0.0.1:4321"]


def test_build_invokes_runner() -> None:
    from tripstacking_website.commands.build import default as build_cmd

    recorded: list[tuple[list[str], Path]] = []

    def fake_runner(cmd: list[str], cwd: Path) -> int:
        recorded.append((cmd, cwd))
        return 0

    exit_code = build_cmd(runner=fake_runner)
    assert exit_code == 0
    assert len(recorded) == 1
    cmd, cwd = recorded[0]
    assert "build" in cmd
    assert cwd.name == "site"


def test_preview_invokes_runner_with_wrangler() -> None:
    from tripstacking_website.commands.preview import default as preview_cmd

    recorded: list[tuple[list[str], Path]] = []
    opened_urls: list[str] = []

    def fake_runner(cmd: list[str], cwd: Path) -> int:
        recorded.append((cmd, cwd))
        return 0

    exit_code = preview_cmd(
        host="127.0.0.1",
        port=4321,
        wrangler=True,
        open_browser=True,
        runner=fake_runner,
        browser_opener=opened_urls.append,
    )
    assert exit_code == 0
    assert len(recorded) == 1
    cmd, cwd = recorded[0]
    assert any("wrangler" in part for part in cmd)
    assert cwd.name == "site"
    assert opened_urls == ["http://127.0.0.1:4321"]


def test_top_level_commands_dry_run(capsys: pytest.CaptureFixture[str]) -> None:
    assert app(["serve", "--dry-run"], result_action="return_value") == 0
    assert "127.0.0.1:4321" in capsys.readouterr().out

    assert app(["build", "--dry-run"], result_action="return_value") == 0
    assert "site" in capsys.readouterr().out.lower()

    assert app(["preview", "--dry-run"], result_action="return_value") == 0
    assert "127.0.0.1:4321" in capsys.readouterr().out


def test_main_entrypoint_and_module_execution(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--version"]) == 0
    assert __version__ in capsys.readouterr().out

    proc = subprocess.run(
        [sys.executable, "-m", "tripstacking_website", "--version"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert __version__ in proc.stdout


def test_register_commands_skips_private_entries(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    from cyclopts import App

    from tripstacking_website.commands import register_commands

    (tmp_path / "_private.py").write_text(
        'def default() -> int:\n    """Private."""\n    return 1\n',
        encoding="utf-8",
    )
    (tmp_path / "ping.py").write_text(
        'def default() -> int:\n    """Ping help."""\n    print("pong")\n    return 0\n',
        encoding="utf-8",
    )

    custom = App(name="test-web")
    register_commands(custom, tmp_path)
    custom(["--help"], result_action="return_value")
    help_out = capsys.readouterr().out
    assert "ping" in help_out
    assert "_private" not in help_out
    assert custom(["ping"], result_action="return_value") == 0
    assert "pong" in capsys.readouterr().out
