"""Optional offline MLflow integration; all experiment results are explicitly synthetic."""
from __future__ import annotations

import argparse
import json

from clarion.v4.mlops_adapter import log_local_experiment, summarize_run


def main() -> int:
    p = argparse.ArgumentParser(description="CLARION local MLOps experiment tracking")
    p.add_argument("--run", required=True)
    p.add_argument("--out", default="artifacts/mlops")
    args = p.parse_args()
    status = log_local_experiment(summarize_run(args.run), destination=args.out)
    print(json.dumps(status, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
