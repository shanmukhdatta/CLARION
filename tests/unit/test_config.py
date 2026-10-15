"""Tests for run profiles (configs/profiles/*.yaml) and their strict loader."""

from __future__ import annotations

from pathlib import Path

import pytest

from clarion.core.config import (
    MAX_PROFILE_BYTES,
    load_analysis_profile,
    load_compute_profile,
    load_run_config,
)
from clarion.core.errors import ConfigError

REPO_PROFILES = Path(__file__).resolve().parents[2] / "configs" / "profiles"

VALID_COMPUTE = """\
schema_version: 1
kind: compute
name: test
description: test compute profile
device: cpu
cpu_fallback: false
network_access: deny
limits:
  max_input_file_mb: 10
  max_workers: 1
"""

VALID_CROSS_LAYER = """\
schema_version: 1
kind: analysis
name: test
description: test analysis profile
analysis_mode: cross_layer
cross_layer_gates:
  min_txid_join_coverage: 0.8
  max_clock_skew_ms: 500
"""


def write_profile(directory: Path, text: str, name: str = "test") -> None:
    (directory / f"{name}.yaml").write_text(text, encoding="utf-8")


# --- The profiles shipped in configs/profiles ---


@pytest.mark.parametrize("name", ["cpu", "gpu"])
def test_shipped_compute_profiles_load(name: str) -> None:
    profile = load_compute_profile(name, REPO_PROFILES)
    assert profile.name == name
    assert profile.network_access == "deny"


@pytest.mark.parametrize("name", ["chain_only", "cross_layer"])
def test_shipped_analysis_profiles_load(name: str) -> None:
    assert load_analysis_profile(name, REPO_PROFILES).name == name


def test_default_run_config_is_cpu_and_chain_only() -> None:
    config = load_run_config(profiles_dir=REPO_PROFILES)
    assert (config.compute.name, config.analysis.name) == ("cpu", "chain_only")
    assert not config.cross_layer_enabled


def test_cross_layer_stays_off_while_gate_thresholds_are_undecided() -> None:
    config = load_run_config(analysis="cross_layer", profiles_dir=REPO_PROFILES)
    assert config.analysis.analysis_mode == "cross_layer"
    assert not config.cross_layer_enabled


def test_cross_layer_turns_on_once_gate_thresholds_are_set(tmp_path: Path) -> None:
    write_profile(tmp_path, VALID_COMPUTE)
    write_profile(tmp_path, VALID_CROSS_LAYER.replace("name: test", "name: gated"), name="gated")
    assert load_run_config(
        compute="test", analysis="gated", profiles_dir=tmp_path
    ).cross_layer_enabled


def test_profiles_cannot_be_changed_after_loading() -> None:
    profile = load_compute_profile("cpu", REPO_PROFILES)
    with pytest.raises(ValueError, match="frozen"):
        profile.device = "cuda"


# --- Invalid settings are rejected, not ignored ---


@pytest.mark.parametrize(
    ("old", "new", "error"),
    [
        ("max_workers: 1", "max_worker: 1", "max_worker"),  # typo = unknown key
        ("network_access: deny", "network_access: allow", "network_access"),
        ("max_workers: 1", "max_workers: '1'", "max_workers"),  # text, not a number
        ("max_workers: 1", "max_workers: 0", "max_workers"),  # must be positive
        ("cpu_fallback: false", "cpu_fallback: true", "cpu_fallback only applies"),
        ("kind: compute", "kind: analysis", "kind"),
        ("name: test", "name: other", "file is named 'test'"),
    ],
)
def test_invalid_compute_setting_is_rejected(
    tmp_path: Path, old: str, new: str, error: str
) -> None:
    assert old in VALID_COMPUTE
    write_profile(tmp_path, VALID_COMPUTE.replace(old, new))
    with pytest.raises(ConfigError, match=error):
        load_compute_profile("test", tmp_path)


@pytest.mark.parametrize(
    ("old", "new", "error"),
    [
        ("min_txid_join_coverage: 0.8", "min_txid_join_coverage: 1.5", "min_txid_join_coverage"),
        ("analysis_mode: cross_layer", "analysis_mode: chain_only", "must set cross_layer_gates"),
        (
            "cross_layer_gates:\n  min_txid_join_coverage: 0.8\n  max_clock_skew_ms: 500\n",
            "cross_layer_gates: null\n",
            "requires cross_layer_gates",
        ),
    ],
)
def test_invalid_analysis_setting_is_rejected(
    tmp_path: Path, old: str, new: str, error: str
) -> None:
    assert old in VALID_CROSS_LAYER
    write_profile(tmp_path, VALID_CROSS_LAYER.replace(old, new))
    with pytest.raises(ConfigError, match=error):
        load_analysis_profile("test", tmp_path)


# --- Unsafe or malformed files are rejected before validation ---


@pytest.mark.parametrize(
    ("text", "error"),
    [
        ("!!python/object/apply:os.system ['echo unsafe']\n", "invalid YAML"),  # code execution
        ("a: &x 1\nb: *x\n", "aliases are not allowed"),  # YAML-bomb building block
        ("a: 1\na: 2\n", "duplicate key 'a'"),
        ("- just\n- a list\n", "top level"),
        ("key: [unclosed\n", "invalid YAML"),
    ],
)
def test_unsafe_or_malformed_yaml_is_rejected(tmp_path: Path, text: str, error: str) -> None:
    write_profile(tmp_path, text)
    with pytest.raises(ConfigError, match=error):
        load_compute_profile("test", tmp_path)


def test_oversized_profile_is_rejected(tmp_path: Path) -> None:
    write_profile(tmp_path, VALID_COMPUTE + "#" * MAX_PROFILE_BYTES)
    with pytest.raises(ConfigError, match="limit"):
        load_compute_profile("test", tmp_path)


def test_missing_profile_is_reported(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="not found"):
        load_compute_profile("absent", tmp_path)


@pytest.mark.parametrize("name", ["../cpu", "CPU", "cpu.yaml", ""])
def test_profile_names_cannot_escape_the_profiles_folder(name: str) -> None:
    with pytest.raises(ConfigError, match="invalid profile name"):
        load_compute_profile(name, REPO_PROFILES)
