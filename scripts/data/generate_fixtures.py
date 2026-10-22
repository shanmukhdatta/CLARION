"""Generate explicit fictional UTXO dataset, keep labels in a truth-only sidecar.

Never feed the truth sidecar to an unsupervised evidence pipeline.
"""
from __future__ import annotations

import argparse
import json

from clarion.application.engine import generate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="data/generated/demo")
    parser.add_argument("--cases", type=int, default=32)
    parser.add_argument("--seed", type=int, default=26)
    args = parser.parse_args()
    print(json.dumps(generate(args.out, args.cases, args.seed), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
