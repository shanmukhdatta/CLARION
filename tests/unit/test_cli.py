"""Tests for the `clarion` command and the packaging that installs it."""

from __future__ import annotations

from importlib.metadata import entry_points, version

import pytest

import clarion
from clarion.cli.main import main


def test_version_flag_prints_version_and_exits_ok(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exit_info:
        main(["--version"])
    assert exit_info.value.code == 0
    assert capsys.readouterr().out == f"clarion {clarion.__version__}\n"


def test_no_arguments_prints_help_and_exits_ok(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 0
    assert capsys.readouterr().out.startswith("usage: clarion")


def test_unknown_argument_fails_with_exit_code_2(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exit_info:
        main(["--bogus"])
    assert exit_info.value.code == 2
    assert "unrecognized arguments: --bogus" in capsys.readouterr().err


def test_installed_version_matches_source_version() -> None:
    # pyproject.toml reads the version from clarion/__init__.py; both must agree.
    assert version("clarion") == clarion.__version__


def test_clarion_console_command_is_registered() -> None:
    (script,) = entry_points(group="console_scripts", name="clarion")
    assert script.value == "clarion.cli.main:main"
