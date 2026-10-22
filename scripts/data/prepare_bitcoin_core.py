"""Convert an APPROVED offline Bitcoin Core verbose JSON transaction export.

Bitcoin Core's RPC JSON is source-specific; this is not a network RPC client.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from clarion.v4.ingest import import_bitcoin_core_tx, load_rows


def _emit(path:Path, rows:list[dict[str,Any]], fields:list[str]) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as fp:
        writer=csv.DictWriter(fp,fieldnames=fields,extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    cli=argparse.ArgumentParser()
    cli.add_argument("--source",required=True,help="JSON array of exported verbosity=2 transactions")
    cli.add_argument("--out",required=True)
    cli.add_argument("--licence",required=True)
    cli.add_argument("--origin",required=True)
    args=cli.parse_args()
    file=Path(args.source)
    records=load_rows(file)
    if not records:
        raise ValueError("empty Bitcoin Core source")
    source_id="bitcoin_core:"+hashlib.sha256(file.read_bytes()).hexdigest()[:16]
    imported=datetime.now(timezone.utc)
    txs,ins,outs=[],[],[]
    for row in records:
        tx,spends,outputs=import_bitcoin_core_tx(
            row,source_id=source_id,available_at=imported
        )
        txs.append(tx.model_dump(mode="json"))
        ins.extend(v.model_dump(mode="json") for v in spends)
        outs.extend(v.model_dump(mode="json") for v in outputs)
    directory=Path(args.out)
    _emit(directory/"transactions.csv",txs,
          ["txid","event_time","available_at","source_id","coinbase","vbytes","fee_sats","block_height","confirmation"])
    _emit(directory/"inputs.csv",ins,
          ["txid","vin","prev_txid","prev_vout","source_id"])
    _emit(directory/"outputs.csv",outs,
          ["txid","vout","value_sats","address","script_type","source_id"])
    (directory/"source_manifest.json").write_text(json.dumps({
        "kind":"bitcoin_core","source_id":source_id,"licence":args.licence,
        "origin":args.origin,"input_sha256":hashlib.sha256(file.read_bytes()).hexdigest(),
        "unknown_prevouts":"MUST remain unknown unless earlier exports are present",
        "no_wallet_ip_inference":True,
    },indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"txs":len(txs),"inputs":len(ins),"outputs":len(outs),"out":str(directory)}))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
