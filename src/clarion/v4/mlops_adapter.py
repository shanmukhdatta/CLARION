"""Local-only experiment metadata and optional MLflow logging.

Experiments are not deployed models. Never log private raw IPs, labels or cases.
"""
from __future__ import annotations

import json
import math
from pathlib import Path


def summarize_run(run_dir: str | Path) -> dict[str, float]:
    from clarion.v4.submission import inspect_run

    report = inspect_run(run_dir)
    return {
        "synthetic_lead_count": float(report["lead_count"]),
        "evidence_graph_edges": float(report["graph_edges"]),
        "evidence_graph_nodes": float(report["graph_nodes"]),
        "max_propagation_points": 25.0,
    }


def log_local_experiment(
    metrics: dict[str, float], *, destination: str | Path,
    name: str = "clarion-synthetic-integration"
) -> dict[str, str]:
    """Record finite aggregate metrics. Optional MLflow uses only local file storage."""
    safe = {k: float(v) for k, v in metrics.items()
            if k.replace("_", "").isalnum() and math.isfinite(float(v))}
    if len(safe) != len(metrics):
        raise ValueError("invalid metric name or nonfinite value")
    root = Path(destination).resolve()
    root.mkdir(parents=True, exist_ok=True)
    record = {"type": "SYNTHETIC_DEMO_ONLY", "name": name, "metrics": safe}
    (root / "experiment.json").write_text(
        json.dumps(record, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    try:
        import mlflow
    except ImportError:
        return {"status": "RECORDED_JSON_MLFLOW_NOT_INSTALLED", "path": str(root / "experiment.json")}
    mlflow.set_tracking_uri((root / "mlruns").as_uri())
    mlflow.set_experiment(name)
    with mlflow.start_run(run_name="offline_synthetic_contract"):
        mlflow.set_tag("evidence_type", "synthetic")
        mlflow.set_tag("calibrated", "false")
        mlflow.log_metrics(safe)
    return {"status": "MLFLOW_LOCAL_RECORDED", "path": str(root / "mlruns")}
