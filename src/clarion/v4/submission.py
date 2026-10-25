"""Offline SIH submission orchestration and independently checkable acceptance evidence.

No synthetic data is called genuine network capture or validated criminal activity.
No model pickle is ever loaded. This module does not mutate source evidence.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def _read_json(path: Path, limit: int = 20_000_000) -> Any:
    if not path.is_file() or path.stat().st_size > limit:
        raise ValueError(f"missing or oversized run artifact: {path.name}")
    return json.loads(path.read_text(encoding="utf-8"))


def model_readiness(model_path: str | Path | None = None) -> dict[str, str]:
    """A fake .pkl/.h5 is not a model. Only the validated local JSON baseline is supported."""
    if model_path is None:
        return {"status": "MODEL_NOT_CONFIGURED", "detail": "Demo uses novelty ranking; train an eligible model separately."}
    path = Path(model_path)
    if not path.exists():
        return {"status": "MODEL_NOT_CONNECTED", "detail": "Selected model artifact was not found."}
    if path.suffix.lower() != ".json":
        return {"status": "UNSUPPORTED_MODEL_FORMAT", "detail": "Never deserialize untrusted pickle/H5 as a placeholder."}
    from clarion.v4.model_artifact import load_model_artifact
    try:
        artifact = load_model_artifact(path)
    except (ValueError, OSError, TypeError, KeyError, json.JSONDecodeError) as exc:
        return {"status": "MODEL_REJECTED", "detail": type(exc).__name__}
    return {
        "status": "EXPERIMENTAL_UNCALIBRATED",
        "detail": str(artifact.get("score_type", "No validated crime probability")),
    }


def inspect_run(run_dir: str | Path, model_path: str | Path | None = None) -> dict[str, Any]:
    """Fail closed on missing evidence, forbidden owner links or score inflation."""
    root = Path(run_dir)
    manifest = _read_json(root / "run_manifest.json")
    graph = _read_json(root / "graph.json")
    leads = _read_json(root / "leads.json")
    if not isinstance(leads, list) or not isinstance(graph, dict):
        raise ValueError("invalid graph/leads artifacts")
    edges = graph.get("edges", [])
    if not isinstance(edges, list):
        raise ValueError("invalid graph edges")
    if any(
        e.get("relation") in {"wallet_owner", "owns_wallet", "ip_owns_address"}
        for e in edges if isinstance(e, dict)
    ):
        raise ValueError("forbidden wallet ownership inference")
    for lead in leads:
        if not isinstance(lead, dict):
            raise ValueError("invalid lead")
        local = float(lead["local_seed_points"])
        prop = float(lead["propagation_points"])
        final = float(lead["risk_points"])
        if not 0 <= local <= 75 or not 0 <= prop <= 25 or abs(local + prop - final) > 0.003:
            raise ValueError("invalid frozen-seed / capped propagation score")
        if lead.get("score_type") != "UNSUPERVISED_RANK_NOT_PROBABILITY":
            raise ValueError("unsupported score type in demo run")
        for name in ("delta", "pi"):
            signal = lead.get(name)
            if not isinstance(signal, dict) or signal.get("status") != "ABSTAIN":
                raise ValueError(f"demo lacks independently validated {name} evidence")
    if len(leads) != manifest.get("n_leads"):
        raise ValueError("manifest/lead-count disagreement")
    return {
        "schema_version": 1,
        "mode": "SYNTHETIC_DEMONSTRATION" if manifest.get("kind") == "EVIDENCE_FIRST_UNSUPERVISED_V4" else "UNVERIFIED_SOURCE",
        "run_manifest_sha256": hashlib.sha256((root / "run_manifest.json").read_bytes()).hexdigest(),
        "lead_count": len(leads),
        "graph_nodes": len(graph.get("nodes", [])),
        "graph_edges": len(edges),
        "result": "VALIDATED_DEMO_ARTIFACT_CONTRACT",
        "model": model_readiness(model_path),
        "constraints": {
            "no_wallet_ip_owner_edge": True,
            "propagation_max_points": 25,
            "delta": "ABSTAIN_UNVERIFIED_PAIRING",
            "pi": "ABSTAIN_UNVERIFIED_GOAL",
            "probability_of_illicit_activity": "NOT_ESTIMATED",
        },
    }


def make_demo(out_dir: str | Path, *, cases: int = 10, seed: int = 26) -> dict[str, Any]:
    """Run the existing generator and the real canonical v4 analysis; no mock lead outputs."""
    from clarion.application.engine import generate
    from clarion.v4.pipeline import run

    if not 6 <= cases <= 50:
        raise ValueError("submission fixture must use 6..50 cases")
    root = Path(out_dir)
    raw = root / "synthetic"
    result = root / "investigation"
    generate(raw, cases=cases, seed=seed)
    run(raw, result, licence="SYNTHETIC_LOCAL", origin="CLARION_GENERATOR")
    report = inspect_run(result)
    (root / "SUBMISSION_STATUS.json").write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    return report
