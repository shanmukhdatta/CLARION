"""Infer uncalibrated *research* scores from a verified local JSON model."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from clarion.v4.model_artifact import load_model_artifact, predict_json_logistic


def main() -> int:
    cli = argparse.ArgumentParser()
    cli.add_argument("--model", required=True)
    cli.add_argument("--features", required=True, help="canonical features.json")
    cli.add_argument("--out", default="artifacts/unvalidated_predictions.json")
    args = cli.parse_args()
    artifact = load_model_artifact(Path(args.model))
    features = json.loads(Path(args.features).read_text(encoding="utf-8"))
    if not isinstance(features, list) or len(features) > 250_000:
        raise ValueError("bounded feature record list required")
    result = predict_json_logistic(artifact, features)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "status": "EXPERIMENTAL_UNCALIBRATED", "model_sha256": artifact["payload_sha256"],
        "predictions": result,
    }, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(out), "predictions": len(result)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
