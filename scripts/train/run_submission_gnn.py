"""Optional GraphSAGE trainer/inference. Requires compatible torch and PyG installation."""
from __future__ import annotations

import argparse
import json

from clarion.v4.gnn_training import infer_graphsage, train_graphsage


def main() -> int:
    p = argparse.ArgumentParser(description="Chronological GraphSAGE research proxy")
    p.add_argument("action", choices=("train", "infer"))
    p.add_argument("--graph", required=True)
    p.add_argument("--model", default="artifacts/models/graphsage_proxy.json")
    p.add_argument("--epochs", type=int, default=12)
    p.add_argument("--cutoff")
    p.add_argument("--source")
    p.add_argument("--target")
    args = p.parse_args()
    if args.action == "train":
        result = train_graphsage(args.graph, args.model, epochs=args.epochs, cutoff=args.cutoff)
    else:
        if not args.source or not args.target:
            p.error("infer requires --source and --target node IDs from graph.json")
        result = infer_graphsage(args.graph, args.model, args.source, args.target)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
