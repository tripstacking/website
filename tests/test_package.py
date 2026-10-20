"""Tests for repository tooling, package metadata, and configuration."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

import tripstacking_website

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_package_version() -> None:
    assert tripstacking_website.__version__ == "0.1.0"


def test_tool_versions_includes_nodejs_pre_commit_and_uv() -> None:
    tool_versions = (REPO_ROOT / ".tool-versions").read_text(encoding="utf-8")
    assert "nodejs 26.2.0" in tool_versions
    assert "pre-commit 4.6.2" in tool_versions
    assert "uv 0.13.3" in tool_versions
    assert "python" not in tool_versions


def test_python_version_is_3_15() -> None:
    python_version = (REPO_ROOT / ".python-version").read_text(encoding="utf-8").strip()
    assert python_version.startswith("3.15")

    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert pyproject["project"]["requires-python"] == ">=3.15"


def test_pre_commit_config_defines_required_hooks() -> None:
    config_path = REPO_ROOT / ".pre-commit-config.yaml"
    assert config_path.exists()
    content = config_path.read_text(encoding="utf-8")
    for required_hook in (
        "end-of-file-fixer",
        "trailing-whitespace",
        "mixed-line-ending",
        "ruff",
        "uv run ty check",
        "pytest",
    ):
        assert required_hook in content


def test_vscode_settings_configures_uv_venv() -> None:
    settings_path = REPO_ROOT / ".vscode" / "settings.json"
    assert settings_path.is_file()
    settings = json.loads(settings_path.read_text(encoding="utf-8"))
    assert settings.get("python.defaultInterpreterPath") == "${workspaceFolder}/.venv/bin/python"
