"""Explicitly map independently documented provider columns to canonical files.

Feature-only external benchmarks MUST NOT be masqueraded as UTXO-level data.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from clarion.v4.ingest import declared_mapping_adapter, load_rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--kind", required=True, choices=("sih", "elliptic_pp", "bitcoinheist"))
    parser.add_argument("--mapping", required=True, help="JSON mapping canonical->provider column")
    parser.add_argument("--required", required=True, nargs="+")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    mapping = json.loads(Path(args.mapping).read_text(encoding="utf-8"))
    if not isinstance(mapping, dict):
        raise ValueError("mapping must be a JSON object")
    rows = declared_mapping_adapter(
        load_rows(Path(args.source)), mapping,
        required=set(args.required), source_kind=args.kind,
    )
    if not rows:
        raise ValueError("empty source")
    target = Path(args.out)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(mapping))
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({"rows": len(rows), "output": str(target), "provider": args.kind}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
