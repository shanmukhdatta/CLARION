"""One-command local synthetic training + inference + canonical CLARION v4 investigation.

Training truth is kept separate and never used in canonical inference. This is a
technical demo of machinery, not independently validated fraud classification.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from clarion.application.engine import generate, investigate
from clarion.application.training_demo import train
from clarion.v4.mlops_adapter import log_local_experiment, summarize_run
from clarion.v4.pipeline import run
from clarion.v4.submission import inspect_run


def execute(output: Path, *, cases: int = 36, seed: int = 26) -> dict[str, object]:
    if not 30 <= cases <= 100:
        raise ValueError("training demonstration requires 30..100 synthetic cases")
    raw = output / "synthetic"
    v4_dir = output / "investigation"
    trained = output / "training"
    legacy = output / "trained_demo_inference"
    generate(raw, cases=cases, seed=seed)
    training = train(raw, trained, seed=seed)
    investigate(raw, legacy, trained / "predictions.json")
    run(raw, v4_dir, licence="SYNTHETIC_LOCAL", origin="CLARION_GENERATOR")
    verification = inspect_run(v4_dir)
    if training.get("kind") != "SYNTHETIC_DEMO_ONLY":
        raise ValueError("model outcome must be identified as synthetic")
    metrics = training.get("metrics", {})
    if not isinstance(metrics, dict) or not metrics:
        raise ValueError("no measured demo training output")
    # A separate observational experiment document. No truth sidecar is included.
    summary = {
        "training_status": "SYNTHETIC_EXPERIMENT_ONLY",
        "model_status": "NO_CALIBRATED_DEPLOYED_MODEL",
        "model_families": training["base_models"],
        "meta_model": training["meta_model"],
        "training_protocol": training["split"],
        "metrics_synthetic_only": metrics,
        "prediction_artifact_sha256": hashlib.sha256(
            (trained / "predictions.json").read_bytes()
        ).hexdigest(),
        "evidence_inspector": verification,
        "important": "Holdout performance is generator-dependent and does NOT establish real Bitcoin illicit classification.",
    }
    status_path = v4_dir / "training_experiment.json"
    status_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    logged = log_local_experiment(
        {**summarize_run(v4_dir), **{
            f"synthetic_{key}": float(value) for key, value in metrics.items()
            if isinstance(value, (float, int))
        }},
        destination=output / "mlops",
    )
    summary["mlops_tracking"] = logged["status"]
    (output / "DEMO_REPORT.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="CLARION full local synthetic demo")
    parser.add_argument("--out", default="artifacts/full_demo")
    parser.add_argument("--cases", type=int, default=36)
    parser.add_argument("--seed", type=int, default=26)
    args = parser.parse_args()
    report = execute(Path(args.out), cases=args.cases, seed=args.seed)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
