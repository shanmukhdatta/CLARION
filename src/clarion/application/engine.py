"""CLARION evidence-first local demonstration engine.

All generated addresses/transactions and ground truth are FICTIONAL. Chain transfers
are backed by exact prevouts, not inferred address-to-address owner identities.
No external HTTP requests are performed by this module.
"""
from __future__ import annotations

import csv
import hashlib
import json
import random
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

MAX_ROWS = 200_000
SATS = 100_000_000


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def _read(path: Path, limit: int = MAX_ROWS) -> list[dict[str, str]]:
    if path.stat().st_size > 80_000_000:
        raise ValueError(f"input exceeds size limit: {path}")
    with path.open("r", newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames:
            raise ValueError("CSV header required")
        result = []
        for i, row in enumerate(reader):
            if i >= limit:
                raise ValueError(f"too many rows: {path}")
            result.append(dict(row))
    return result


def _csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def generate(directory: str | Path, cases: int = 90, seed: int = 26) -> dict[str, Any]:
    """Deterministic, deliberately simplistic ledger plus independent sensor logs.

    Separate truth sidecar is not loaded by inference. A case is a 3-transaction
    spending episode funded by a fictional unspent coinbase-like transaction.
    """
    if not 6 <= cases <= 5000:
        raise ValueError("cases must be between 6 and 5000")
    root = Path(directory)
    rng = random.Random(seed)
    txs: list[dict[str, Any]] = []
    inp: list[dict[str, Any]] = []
    out: list[dict[str, Any]] = []
    observations: list[dict[str, Any]] = []
    truth: list[dict[str, Any]] = []
    base = datetime(2025, 1, 1, tzinfo=timezone.utc)
    for case in range(cases):
        # Mix case order without encoding a synthetic class in a case identifier.
        suspicious = rng.random() < 0.43
        case_id = f"case-{case:05d}"
        amount = rng.randrange(25_000_000, 280_000_000)
        fee = rng.randint(400, 2500)
        clock = base + timedelta(minutes=case * 30)
        parent = _sha(f"{seed}|{case}|fund")
        txs.append({"txid": parent, "time": clock.isoformat(), "case_id": case_id, "fee_sats": 0, "vbytes": 120, "coinbase": 1})
        output_addr = f"addr_{_sha(f'{seed}/fund/{case}')[:16]}"
        out.append({"txid": parent, "vout": 0, "address": output_addr, "value_sats": amount})
        for step in range(3):
            # A plausible change/peel fraction; ambiguous legitimate behavior overlaps.
            small_fraction = rng.uniform(.012, .12) if suspicious else rng.uniform(.09, .55)
            if rng.random() < .18:  # hard negatives / difficult positives
                small_fraction = rng.uniform(.07, .28)
            payment = int((amount - fee) * small_fraction)
            change = amount - fee - payment
            txid = _sha(f"{seed}|{case}|{step}|tx")
            clock += timedelta(seconds=rng.randint(20, 190) if suspicious else rng.randint(80, 900))
            txs.append({"txid": txid, "time": clock.isoformat(), "case_id": case_id, "fee_sats": fee, "vbytes": rng.randint(140, 280), "coinbase": 0})
            inp.append({"txid": txid, "vin": 0, "prev_txid": parent, "prev_vout": 0})
            continuation = f"addr_{_sha(f'{seed}/{case}/{step}/next')[:16]}"
            recipient = f"addr_{_sha(f'{seed}/{case}/{step}/pay')[:16]}"
            out.append({"txid": txid, "vout": 0, "address": continuation, "value_sats": change})
            out.append({"txid": txid, "vout": 1, "address": recipient, "value_sats": payment})
            # Independent sensor identities, and repeated observation as a dedup test.
            for sensor_index in range(rng.choice([1, 1, 2])):
                sensor = f"sensor-{sensor_index}"
                host = f"192.0.2.{(case * 3 + step * 5 + sensor_index) % 240 + 1}"
                observed = {"sensor_id": sensor, "txid": txid, "host": host, "time": (clock + timedelta(seconds=4 + sensor_index)).isoformat(), "event": "inv"}
                observations.append(observed)
                if step == 1:
                    observations.append(dict(observed))
            truth.append({"txid": txid, "case_id": case_id, "label": int(suspicious), "scenario": "peel_like" if suspicious else "ordinary_payment"})
            parent, amount = txid, change
    _csv(root / "transactions.csv", txs, ["txid", "time", "case_id", "fee_sats", "vbytes", "coinbase"])
    _csv(root / "inputs.csv", inp, ["txid", "vin", "prev_txid", "prev_vout"])
    _csv(root / "outputs.csv", out, ["txid", "vout", "address", "value_sats"])
    _csv(root / "observations.csv", observations, ["sensor_id", "txid", "host", "time", "event"])
    _csv(root / "truth_SYNTHETIC_ONLY.csv", truth, ["txid", "case_id", "label", "scenario"])
    manifest = {"kind": "SYNTHETIC_FICTIONAL", "seed": seed, "case_count": cases,
                "label_uses": "demo tests/training ONLY; not real-world criminality",
                "transactions": len(txs), "network_is_not_ownership": True}
    _json(root / "source_manifest.json", manifest)
    return manifest


def _time(text: str) -> datetime:
    t = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if t.tzinfo is None:
        raise ValueError("timestamp must include timezone")
    return t.astimezone(timezone.utc)


def _sats(value: str) -> int:
    if not value.isdigit() or int(value) < 0:
        raise ValueError("value must be a nonnegative integer number of satoshis")
    return int(value)


def load(directory: str | Path, cutoff: datetime | None = None) -> dict[str, Any]:
    """Strict reference validation and as-of snapshot; never load truth into evidence."""
    root = Path(directory)
    sources = {n: root / f"{n}.csv" for n in ("transactions", "inputs", "outputs", "observations")}
    raw = {n: _read(path) for n, path in sources.items()}
    times = {}
    txs: dict[str, dict[str, Any]] = {}
    for tx in raw["transactions"]:
        txid = tx["txid"]
        if len(txid) != 64 or any(c not in "0123456789abcdef" for c in txid) or txid in txs:
            raise ValueError(f"invalid or duplicate transaction id: {txid}")
        stamp = _time(tx["time"])
        if cutoff is not None and stamp > cutoff:
            continue
        times[txid] = stamp
        txs[txid] = {"txid": txid, "time": stamp.isoformat(), "case_id": tx["case_id"],
                      "vbytes": _sats(tx["vbytes"]), "fee_sats": _sats(tx["fee_sats"]),
                      "coinbase": tx["coinbase"] == "1"}
    outputs: dict[tuple[str, int], dict[str, Any]] = {}
    for row in raw["outputs"]:
        txid = row["txid"]
        if txid not in txs:
            continue
        key = (txid, _sats(row["vout"]))
        if key in outputs:
            raise ValueError("duplicate outpoint")
        outputs[key] = {"address": row["address"], "value_sats": _sats(row["value_sats"]), "txid": txid, "vout": key[1]}
    inputs = defaultdict(list)
    for row in raw["inputs"]:
        if row["txid"] in txs:
            inputs[row["txid"]].append((row["prev_txid"], _sats(row["prev_vout"])))
    spent = set()
    links = []
    features = []
    for txid, tx in sorted(txs.items(), key=lambda kv: (kv[1]["time"], kv[0])):
        prevs = inputs[txid]
        own = [o for key, o in sorted(outputs.items()) if key[0] == txid]
        if not own:
            raise ValueError(f"transaction without outputs: {txid}")
        amount_out = sum(o["value_sats"] for o in own)
        if tx["coinbase"]:
            if prevs:
                raise ValueError("coinbase-like funding must not have inputs")
            continue
        if not prevs:
            raise ValueError(f"ordinary tx lacks inputs: {txid}")
        amount_in = 0
        for prev in prevs:
            if prev in spent:
                raise ValueError("duplicate prevout spend")
            spent.add(prev)
            if prev not in outputs:
                raise ValueError(f"unresolved prevout or future data: {prev}")
            if times[prev[0]] > times[txid]:
                raise ValueError("prevout is later than spending tx")
            amount_in += outputs[prev]["value_sats"]
            links.append({"source": prev[0], "target": txid, "type": "spends-outpoint",
                          "outpoint": f"{prev[0]}:{prev[1]}", "amount_sats": outputs[prev]["value_sats"],
                          "time": tx["time"], "evidence_id": f"input:{txid}:{len(links)}"})
        if amount_in != amount_out + tx["fee_sats"]:
            raise ValueError(f"UTXO conservation failed: {txid}")
        values = sorted((o["value_sats"] for o in own), reverse=True)
        prev_time = min(times[p[0]] for p in prevs)
        features.append({"txid": txid, "time": tx["time"], "case_id": tx["case_id"],
                         "input_sats": amount_in, "fee_rate": tx["fee_sats"] / max(1, tx["vbytes"]),
                         "output_count": len(own), "input_count": len(prevs),
                         "largest_output_share": values[0] / amount_out if amount_out else 0.0,
                         "smallest_output_share": values[-1] / amount_out if amount_out else 0.0,
                         "age_seconds": max(0., (_time(tx["time"]) - prev_time).total_seconds())})
    valid = set(txs)
    relays = {}
    for row in raw["observations"]:
        if row["txid"] not in valid or (cutoff is not None and _time(row["time"]) > cutoff):
            continue
        _time(row["time"])
        key = (row["sensor_id"], row["host"], row["txid"], row["event"])
        relays.setdefault(key, row)
    wire = [{"source": f"host:{r['host']}", "target": r["txid"], "type": "observed-relay",
             "time": r["time"], "evidence_id": f"sensor:{r['sensor_id']}:{i}",
             "sensor_id": r["sensor_id"]} for i, r in enumerate(relays.values())]
    # Demonstration only: network evidence cannot be mapped to an owner by observation.
    readiness = {"analysis_mode": "CHAIN_ONLY", "wire_observation_count": len(wire),
                 "exact_txid_joined_observations": len(wire),
                 "cross_layer_dependence_verified": False,
                 "reason": "no independently validated chain–wire dependence or origin ground truth"}
    return {"transactions": list(txs.values()), "features": features, "links": links, "wire": wire,
            "outputs": list(outputs.values()), "readiness": readiness,
            "sources": {n: hashlib.sha256(path.read_bytes()).hexdigest() for n, path in sources.items()}}


def entity_hypotheses(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Conservative common-input heuristic; no ownership inference from relay hosts."""
    # Synthetic episodes have single-input transactions; no forced merges are made.
    return []


def motifs(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Find strictly ordered 3-step peel-like UTXO paths, with witnesses."""
    tx_by_id = {t["txid"]: t for t in data["transactions"]}
    feat = {f["txid"]: f for f in data["features"]}
    parent = {e["target"]: e["source"] for e in data["links"]}
    result = []
    for txid, f in feat.items():
        path = [txid]
        while len(path) < 3 and path[-1] in parent and parent[path[-1]] in feat:
            path.append(parent[path[-1]])
        if len(path) < 3:
            continue
        path.reverse()
        if any(feat[p]["largest_output_share"] < .78 for p in path):
            continue
        if len({tx_by_id[p]["case_id"] for p in path}) != 1:
            continue
        result.append({"kind": "peel-like", "subject": txid, "witness_txids": path,
                       "evidence_type": "value-flow-candidate", "benign_alternative": "wallet change or payment batching"})
    return result


def risk_propagation(data: dict[str, Any], seeds: dict[str, float], max_hops: int = 3) -> dict[str, Any]:
    """Bounded, directed, snapshot-only propagation; no risk flows from hosts.

    A downstream case receives at most 25 score points of exposure, with no
    feedback loop. All weights come from frozen pass-one seeds.
    """
    if max_hops < 1 or max_hops > 6:
        raise ValueError("max_hops must be in [1,6]")
    adj = defaultdict(list)
    for e in data["links"]:
        adj[e["source"]].append((e["target"], float(e["amount_sats"])))
    contribution = defaultdict(float)
    paths: dict[str, list[str]] = {}
    for seed, risk in seeds.items():
        if risk < 55:
            continue
        frontier = [(seed, 1.0, [seed])]
        for _ in range(max_hops):
            next_frontier = []
            for at, weight, path in frontier:
                children = adj.get(at, [])
                denominator = max(1., sum(amount for _, amount in children))
                for target, amount in children:
                    if target in path:
                        continue
                    w = weight * .5 * min(1., amount / denominator)
                    c = min(25., risk * .25 * w)
                    contribution[target] = min(25., contribution[target] + c)
                    if target not in paths or c > 1:
                        paths[target] = path + [target]
                    next_frontier.append((target, w, path + [target]))
            frontier = next_frontier
    return {"points": dict(contribution), "witness_paths": paths, "max_hops": max_hops,
            "capacity_points": 25, "seed_count": sum(r >= 55 for r in seeds.values())}


def _load_predictions(path: Path) -> tuple[dict[str, float], str]:
    if not path.exists():
        return {}, "rules-only (no trained model)"
    obj = json.loads(path.read_text(encoding="utf-8"))
    return {p["txid"]: float(p["score"]) for p in obj.get("predictions", [])}, obj.get("score_type", "unknown")


def investigate(source: str | Path, target: str | Path, predictions_file: str | Path | None = None,
                cutoff: str | None = None) -> dict[str, Any]:
    """Run the chain-only dossier with immutable pass-1 seeds then pass-2 fusion."""
    snap = load(source, _time(cutoff) if cutoff else None)
    pattern_list = motifs(snap)
    pattern_ids = {m["subject"] for m in pattern_list}
    predictions, prediction_type = _load_predictions(Path(predictions_file)) if predictions_file else ({}, "rules-only")
    frozen: dict[str, float] = {}
    contributions: dict[str, Any] = {}
    for feat in snap["features"]:
        tx = feat["txid"]
        indicators = {
            "fast_spend": 20 if feat["age_seconds"] < 160 else 0,
            "dominant_continuation": 25 if feat["largest_output_share"] > .85 else 0,
            "peel_motif": 20 if tx in pattern_ids else 0,
            "fee_rate_extreme": 10 if feat["fee_rate"] > 13 else 0,
        }
        rules = min(75., float(sum(indicators.values())))
        # Model scores affect investigative ranking, not validated illicit probability.
        model = predictions.get(tx)
        local = min(100., (rules * .65 + (model * .35 if model is not None else rules * .35)))
        frozen[tx] = local
        contributions[tx] = {"rules": indicators, "model_ranking": model, "local_score": round(local, 3)}
    propagation = risk_propagation(snap, frozen)
    leads = []
    for f in snap["features"]:
        tx = f["txid"]
        exposure = min(25., propagation["points"].get(tx, 0.))
        total = min(100., .75 * frozen[tx] + exposure)
        leads.append({"txid": tx, "case_id": f["case_id"], "time": f["time"],
                      "risk_points": round(total, 3), "priority": "P1" if total >= 75 else "P2" if total >= 50 else "P3" if total >= 25 else "P4",
                      "local_seed_points": round(frozen[tx], 3), "propagation_points": round(exposure, 3),
                      "delta": {"status": "ABSTAIN", "reason": "unverified independent paired dependence"},
                      "pi": {"status": "ABSTAIN", "reason": "no verified controlled economic objective"},
                      "explanation": contributions[tx], "witness_path": propagation["witness_paths"].get(tx, []),
                      "label": None})
    leads.sort(key=lambda x: (-x["risk_points"], x["time"], x["txid"]))
    target = Path(target)
    _json(target / "leads.json", leads)
    _json(target / "graph.json", {"nodes": [{"id": t["txid"], "type": "Transaction"} for t in snap["transactions"]] +
           [{"id": e["source"], "type": "Host"} for e in snap["wire"]],
           "edges": snap["links"] + snap["wire"]})
    _json(target / "motifs.json", pattern_list)
    _json(target / "propagation.json", propagation)
    _json(target / "entities.json", entity_hypotheses(snap))
    _csv(target / "leads.csv", leads, ["txid", "case_id", "time", "risk_points", "priority", "local_seed_points", "propagation_points"])
    manifest = {"status": "DEMO_CHAIN_ONLY", "kind": "INVESTIGATIVE_LEADS_NOT_GUILT",
                "training_score_type": prediction_type, "readiness": snap["readiness"],
                "n_leads": len(leads), "n_motifs": len(pattern_list), "n_chain_edges": len(snap["links"]),
                "n_wire_observations": len(snap["wire"]), "data_source_hashes": snap["sources"],
                "cutoff": cutoff, "unvalidated_real_world_performance": True}
    _json(target / "run_manifest.json", manifest)
    return manifest
