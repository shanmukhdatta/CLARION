"""Reproducible canonical experiment CLI, labels are training-only."""
from __future__ import annotations

import argparse
import json

from clarion.v4.pipeline import train_from_canonical


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--data",required=True)
    p.add_argument("--out",default="artifacts/v4_training")
    p.add_argument("--licence",required=True)
    p.add_argument("--origin",required=True)
    p.add_argument("--seed",type=int,default=26)
    args=p.parse_args()
    report=train_from_canonical(args.data,args.out,licence=args.licence,
                                origin=args.origin,seed=args.seed)
    print(json.dumps(report,indent=2,default=str))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
