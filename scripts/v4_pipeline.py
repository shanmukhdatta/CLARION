"""Static CLI for source-to-artifact CLARION v4 analysis.

Run only after validating source licence, access permission and schema.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime

from clarion.v4.pipeline import run, train_from_canonical


def main() -> int:
    p = argparse.ArgumentParser(description="CLARION v4 offline evidence pipeline")
    p.add_argument("command", choices=("analyze", "train"))
    p.add_argument("--data", required=True, help="canonical local source folder")
    p.add_argument("--out", default="artifacts/v4_run")
    p.add_argument("--licence", required=True, help="dataset licence or permission record")
    p.add_argument("--origin", required=True, help="dataset publisher/provenance")
    p.add_argument("--cutoff", default=None, help="UTC ISO8601 cutoff")
    p.add_argument("--min-join-coverage", type=float, default=None)
    p.add_argument("--max-clock-uncertainty-ms", type=int, default=None)
    args = p.parse_args()
    if args.command == "train":
        manifest = train_from_canonical(args.data, args.out, licence=args.licence, origin=args.origin)
    else:
        when = datetime.fromisoformat(args.cutoff.replace("Z", "+00:00")) if args.cutoff else None
        manifest = run(
            args.data, args.out, licence=args.licence, origin=args.origin, cutoff=when,
            min_join_coverage=args.min_join_coverage,
            max_clock_uncertainty_ms=args.max_clock_uncertainty_ms,
        )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
