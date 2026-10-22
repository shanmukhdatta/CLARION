"""Fit and export a safe JSON logistic experiment from locally labeled canonical data."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from clarion.v4.graph import build_snapshot, feature_rows
from clarion.v4.ingest import import_canonical
from clarion.v4.model_artifact import fit_json_logistic, save_model_artifact


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="authorized canonical folder")
    parser.add_argument("--licence", required=True)
    parser.add_argument("--origin", required=True)
    parser.add_argument("--out", default="artifacts/training_json")
    parser.add_argument("--seed", type=int, default=26)
    args = parser.parse_args()
    data = import_canonical(args.data, licence=args.licence, origin=args.origin,
                            include_labels=True)
    if not data.labels or not data.transactions:
        raise ValueError("no eligible labels/transactions present")
    cutoff = max(t.available_at for t in data.transactions)
    snapshot = build_snapshot(data.transactions, data.inputs, data.outputs,
                              cutoff=cutoff, source_hashes=data.hashes)
    labels = {label.subject_id: (label.value, label.available_at.isoformat())
              for label in data.labels if label.subject_type == "transaction"}
    artifact, report = fit_json_logistic(
        feature_rows(snapshot), labels, source_hashes=data.hashes,
        evaluation_time=cutoff.isoformat(), seed=args.seed,
    )
    out = Path(args.out)
    save_model_artifact(out / "logistic_model.json", artifact)
    (out / "evaluation.json").write_text(json.dumps(report, indent=2) + "\n",
                                        encoding="utf-8")
    print(json.dumps({"model": str(out / "logistic_model.json"), **report}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
