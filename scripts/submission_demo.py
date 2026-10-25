"""Generate and audit a real CLARION synthetic vertical slice; no fabricated outputs."""
from __future__ import annotations

import argparse
import json
from clarion.v4.submission import inspect_run, make_demo



def main() -> int:
    parser = argparse.ArgumentParser(description="CLARION synthetic submission acceptance")
    parser.add_argument("action", choices=("run", "inspect"))
    parser.add_argument("--out", default="artifacts/submission_demo")
    parser.add_argument("--cases", type=int, default=10)
    parser.add_argument("--seed", type=int, default=26)
    args = parser.parse_args()
    report = (make_demo(args.out, cases=args.cases, seed=args.seed)
              if args.action == "run" else inspect_run(args.out + "/investigation"))
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
