"""CLARION local demo console entry point; run as `python -m clarion.cli.main`."""
from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from clarion import __version__
from clarion.application.engine import generate, investigate, load


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="clarion", description="Offline Bitcoin forensic demo (not a crime classifier).")
    parser.add_argument("--version", action="version", version=f"clarion {__version__}")
    sub = parser.add_subparsers(dest="command")
    gen = sub.add_parser("generate-demo", help="generate fictional Bitcoin UTXO + sensor CSV")
    gen.add_argument("--out", default="data/generated/demo")
    gen.add_argument("--cases", type=int, default=90)
    gen.add_argument("--seed", type=int, default=26)
    check = sub.add_parser("validate", help="validate canonical CSV and exact prevouts")
    check.add_argument("--data", default="data/generated/demo")
    train_p = sub.add_parser("train-demo", help="time-safe OOF training on synthetic cases")
    train_p.add_argument("--data", default="data/generated/demo")
    train_p.add_argument("--out", default="artifacts/demo_training")
    score = sub.add_parser("investigate", help="write graph, leads and auditable dossier")
    score.add_argument("--data", default="data/generated/demo")
    score.add_argument("--out", default="artifacts/demo_run")
    score.add_argument("--predictions", default=None)
    score.add_argument("--cutoff", default=None)
    serve = sub.add_parser("serve", help="serve read-only dashboard on localhost")
    serve.add_argument("--run", default="artifacts/demo_run")
    serve.add_argument("--port", type=int, default=8000)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command is None:
        build_parser().print_help()
        return 0
    if args.command == "generate-demo":
        result = generate(args.out, args.cases, args.seed)
    elif args.command == "validate":
        snap = load(args.data)
        result = {"transactions": len(snap["transactions"]), "edges": len(snap["links"]), "readiness": snap["readiness"]}
    elif args.command == "train-demo":
        from clarion.application.training_demo import train
        result = train(args.data, args.out)
    elif args.command == "investigate":
        result = investigate(args.data, args.out, args.predictions, args.cutoff)
    elif args.command == "serve":
        import uvicorn
        from clarion.api.main import create_app
        uvicorn.run(create_app(Path(args.run)), host="127.0.0.1", port=args.port, access_log=False)
        return 0
    else:
        raise RuntimeError("unknown command")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
