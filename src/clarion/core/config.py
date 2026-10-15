"""Load and validate CLARION run profiles from configs/profiles/*.yaml.

A run combines two profiles:

* a **compute** profile (cpu.yaml, gpu.yaml): device, CPU fallback, resource limits;
* an **analysis** profile (chain_only.yaml, cross_layer.yaml): chain-only or
  cross-layer mode, plus the evidence-quality gates cross-layer analysis must pass.

Validation fails closed: unknown or misspelled keys, wrong types, YAML tags,
aliases or duplicate keys, and any setting that would allow network access are
rejected with a ConfigError instead of being silently ignored.
"""

from __future__ import annotations

import re
from collections.abc import Hashable
from pathlib import Path
from typing import Annotated, Any, Literal, Self, TypeVar

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from clarion.core.errors import ConfigError

# Relative to the current directory (the repository root during development).
# Where profiles live on an installed Linux machine is decided with packaging in P5.
DEFAULT_PROFILES_DIR = Path("configs") / "profiles"
MAX_PROFILE_BYTES = 64 * 1024
_PROFILE_NAME = re.compile(r"[a-z0-9_]+")


class _StrictModel(BaseModel):
    # extra="forbid": typos are errors. strict: "4" is not accepted where 4 is expected.
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class ResourceLimits(_StrictModel):
    max_input_file_mb: Annotated[int, Field(gt=0)]
    max_workers: Annotated[int, Field(gt=0)]


class ComputeProfile(_StrictModel):
    schema_version: Literal[1]
    kind: Literal["compute"]
    name: str
    description: str
    device: Literal["cpu", "cuda"]
    cpu_fallback: bool
    network_access: Literal["deny"]  # CLARION never needs the network at run time
    limits: ResourceLimits

    @model_validator(mode="after")
    def _fallback_only_for_cuda(self) -> Self:
        if self.device == "cpu" and self.cpu_fallback:
            raise ValueError("cpu_fallback only applies when device is 'cuda'")
        return self


class CrossLayerGates(_StrictModel):
    """Minimum evidence quality before chain and network data may be combined.

    The thresholds are open decision D06 (docs/architecture/REQUIREMENTS_AUDIT.md).
    ``None`` means "not decided yet": the gate fails closed and the run stays chain-only.
    """

    min_txid_join_coverage: Annotated[float, Field(ge=0.0, le=1.0)] | None
    max_clock_skew_ms: Annotated[int, Field(ge=0)] | None

    @property
    def decided(self) -> bool:
        return self.min_txid_join_coverage is not None and self.max_clock_skew_ms is not None


class AnalysisProfile(_StrictModel):
    schema_version: Literal[1]
    kind: Literal["analysis"]
    name: str
    description: str
    analysis_mode: Literal["chain_only", "cross_layer"]
    cross_layer_gates: CrossLayerGates | None

    @model_validator(mode="after")
    def _gates_match_mode(self) -> Self:
        if self.analysis_mode == "cross_layer" and self.cross_layer_gates is None:
            raise ValueError("analysis_mode 'cross_layer' requires cross_layer_gates")
        if self.analysis_mode == "chain_only" and self.cross_layer_gates is not None:
            raise ValueError("analysis_mode 'chain_only' must set cross_layer_gates: null")
        return self


class RunConfig(_StrictModel):
    compute: ComputeProfile
    analysis: AnalysisProfile

    @property
    def cross_layer_enabled(self) -> bool:
        """True only if cross-layer was requested and every gate threshold is decided.

        Checking the actual data against these thresholds is readiness work (P1.4).
        """
        gates = self.analysis.cross_layer_gates
        return self.analysis.analysis_mode == "cross_layer" and gates is not None and gates.decided


class _StrictSafeLoader(yaml.SafeLoader):
    """yaml.SafeLoader (no code-executing tags) that also rejects aliases and duplicate keys.

    Aliases enable "billion laughs" expansion attacks; duplicate keys let a later line
    silently override an earlier one.
    """

    def compose_node(self, parent: yaml.Node | None, index: Any) -> yaml.Node | None:
        if self.check_event(yaml.AliasEvent):
            event = self.peek_event()  # type: ignore[no-untyped-call]  # unannotated in types-PyYAML
            raise yaml.YAMLError(f"YAML aliases are not allowed{event.start_mark}")
        return super().compose_node(parent, index)

    def construct_mapping(self, node: yaml.MappingNode, deep: bool = False) -> dict[Any, Any]:
        seen: set[Hashable] = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            if isinstance(key, Hashable):
                if key in seen:
                    raise yaml.YAMLError(f"duplicate key {key!r}{key_node.start_mark}")
                seen.add(key)
        return super().construct_mapping(node, deep=deep)


def _read_yaml_mapping(path: Path) -> dict[str, Any]:
    try:
        size = path.stat().st_size
    except FileNotFoundError:
        raise ConfigError(f"profile file not found: {path}") from None
    if size > MAX_PROFILE_BYTES:
        raise ConfigError(f"{path}: file is {size} bytes; the limit is {MAX_PROFILE_BYTES}")
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ConfigError(f"{path}: not valid UTF-8 text") from exc
    loader = _StrictSafeLoader(text)
    try:
        data = loader.get_single_data()
    except yaml.YAMLError as exc:
        raise ConfigError(f"{path}: invalid YAML: {exc}") from exc
    finally:
        loader.dispose()
    if not isinstance(data, dict):
        raise ConfigError(f"{path}: expected 'key: value' settings at the top level")
    return data


_Profile = TypeVar("_Profile", ComputeProfile, AnalysisProfile)


def _load_profile(name: str, profiles_dir: Path, model: type[_Profile]) -> _Profile:
    if not _PROFILE_NAME.fullmatch(name):
        raise ConfigError(
            f"invalid profile name {name!r}: use lowercase letters, digits and '_' only"
        )
    path = profiles_dir / f"{name}.yaml"
    data = _read_yaml_mapping(path)
    try:
        profile = model.model_validate(data)
    except ValidationError as exc:
        raise ConfigError(f"{path}: invalid {model.__name__}:\n{exc}") from exc
    if profile.name != name:
        raise ConfigError(f"{path}: name is {profile.name!r} but the file is named {name!r}")
    return profile


def load_compute_profile(name: str, profiles_dir: Path = DEFAULT_PROFILES_DIR) -> ComputeProfile:
    return _load_profile(name, profiles_dir, ComputeProfile)


def load_analysis_profile(name: str, profiles_dir: Path = DEFAULT_PROFILES_DIR) -> AnalysisProfile:
    return _load_profile(name, profiles_dir, AnalysisProfile)


def load_run_config(
    compute: str = "cpu",
    analysis: str = "chain_only",
    profiles_dir: Path = DEFAULT_PROFILES_DIR,
) -> RunConfig:
    """Load a compute + analysis profile pair. Defaults to the safest setup: CPU, chain-only."""
    return RunConfig(
        compute=load_compute_profile(compute, profiles_dir),
        analysis=load_analysis_profile(analysis, profiles_dir),
    )
