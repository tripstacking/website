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
    assert "themes" in captured.out
    assert "serve" in captured.out
    assert "build" in captured.out


def test_themes_list_command(capsys: pytest.CaptureFixture[str]) -> None:
    result = app(["themes", "list"], result_action="return_value")
    captured = capsys.readouterr()
    out = captured.out.lower()
    for theme_name in ("nova", "zenith", "atlas", "galaxy", "amplify"):
        assert theme_name in out
    assert "4321" in out
    assert "4325" in out
    assert result == 0


def test_themes_serve_single_dry_run(capsys: pytest.CaptureFixture[str]) -> None:
    result = app(
        ["themes", "serve", "--theme", "nova", "--host", "127.0.0.1", "--port", "4321", "--dry-run"],
        result_action="return_value",
    )
    captured = capsys.readouterr()
    assert "nova" in captured.out.lower()
    assert "127.0.0.1:4321" in captured.out
    assert result == 0


def test_themes_serve_all_invokes_multi_runner() -> None:
    from tripstacking_website.commands.themes.serve import default as themes_serve

    recorded_specs: list[tuple[str, list[str], Path]] = []
    opened_urls: list[str] = []

    def fake_multi_runner(tasks: list[tuple[str, list[str], Path]]) -> int:
        recorded_specs.extend(tasks)
        return 0

    exit_code = themes_serve(
        theme="all",
        host="127.0.0.1",
        open_browser=True,
        multi_runner=fake_multi_runner,
        browser_opener=opened_urls.append,
    )
    assert exit_code == 0
    assert len(recorded_specs) == 5
    names = [item[0] for item in recorded_specs]
    assert names == ["nova", "zenith", "atlas", "galaxy", "amplify"]
    assert len(opened_urls) == 5
    assert "http://127.0.0.1:4321" in opened_urls
    assert "http://127.0.0.1:4325" in opened_urls


def test_themes_build_invokes_runner() -> None:
    from tripstacking_website.commands.themes.build import default as themes_build

    recorded: list[tuple[list[str], Path]] = []

    def fake_runner(cmd: list[str], cwd: Path) -> int:
        recorded.append((cmd, cwd))
        return 0

    exit_code = themes_build(theme="nova", runner=fake_runner)
    assert exit_code == 0
    assert len(recorded) == 1
    cmd, cwd = recorded[0]
    assert "build" in cmd
    assert cwd.name == "nova"


def test_themes_preview_invokes_multi_runner() -> None:
    from tripstacking_website.commands.themes.preview import default as themes_preview

    recorded_specs: list[tuple[str, list[str], Path]] = []

    def fake_multi_runner(tasks: list[tuple[str, list[str], Path]]) -> int:
        recorded_specs.extend(tasks)
        return 0

    exit_code = themes_preview(
        theme="all",
        host="127.0.0.1",
        wrangler=True,
        multi_runner=fake_multi_runner,
    )
    assert exit_code == 0
    assert len(recorded_specs) == 5
    assert any("wrangler" in part for part in recorded_specs[0][1])


def test_top_level_serve_and_build_commands(capsys: pytest.CaptureFixture[str]) -> None:
    assert app(["serve", "--theme", "zenith", "--dry-run"], result_action="return_value") == 0
    assert "zenith" in capsys.readouterr().out.lower()

    assert app(["build", "--theme", "atlas", "--dry-run"], result_action="return_value") == 0
    assert "atlas" in capsys.readouterr().out.lower()


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
