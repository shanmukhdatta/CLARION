"""Optional *research* GraphSAGE/GAT snapshot challenger (no pretrained weights).

Using this file never claims that the model is trained or scientifically valid.
A temporal fold-based benchmark must be conducted separately.
"""
from __future__ import annotations

import argparse
import json

from clarion.v4.pipeline import load_json
from clarion.v4.ml import optional_pyg_encoder


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--snapshot-tensors",required=True,
                   help="offline JSON with x[node,features], edge_index[2,edges], source cutoff")
    p.add_argument("--kind",choices=("sage","gat"),default="sage")
    p.add_argument("--epochs",type=int,default=20)
    p.add_argument("--out",default="artifacts/gnn_embedding.json")
    args=p.parse_args()
    from pathlib import Path
    obj=load_json(Path(args.snapshot_tensors))
    if not all(key in obj for key in ("x","edge_index","cutoff")):
        raise ValueError("input requires x, edge_index, and approved as-of cutoff")
    embedding=optional_pyg_encoder(
        obj["x"],obj["edge_index"],model_kind=args.kind,epochs=args.epochs
    )
    output=Path(args.out)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps({
        "kind":"UNSUPERVISED_GRAPH_CHALLENGER_NOT_CLASSIFIER",
        "cutoff":obj["cutoff"],
        "source_snapshot_hash":obj.get("source_snapshot_hash"),
        "model_kind":args.kind,
        "embedding":embedding.tolist(),
        "not_validated_for_criminality":True,
    },indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"embeddings":int(embedding.shape[0]),"dimensions":int(embedding.shape[1]),"path":str(output)}))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
