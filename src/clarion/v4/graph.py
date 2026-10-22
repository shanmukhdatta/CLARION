"""As-of typed cross-layer evidence graph; exact UTXO transfer accounting.

Host relays attach to transactions as observations only, NEVER wallet control.
Timestamp UTC and source provenance are carried through each edge.
"""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from datetime import datetime

from clarion.v4.contracts import (
    Edge,
    Input,
    Mode,
    Output,
    Readiness,
    Snapshot,
    Tx,
    WireObservation,
    evidence_id,
    utc,
)


def build_snapshot(
    transactions: Iterable[Tx], inputs: Iterable[Input], outputs: Iterable[Output],
    wire: Iterable[WireObservation] = (), *,
    cutoff: datetime, source_hashes: dict[str, str] | None = None,
    labels_available: bool = False, min_join_coverage: float | None = None,
    max_clock_uncertainty_ms: int | None = None,
) -> Snapshot:
    """Cut at available_at, not event_time alone; refuse future dependent edges.

    Cross-layer mode is only ELIGIBLE if gates are explicitly configured; this
    does NOT assert that statistical dependence or causation has been validated.
    """
    cutoff = utc(cutoff)
    selected_tx = [v for v in transactions if v.available_at <= cutoff and v.event_time <= cutoff]
    tx = {v.txid: v for v in selected_tx}
    if len(tx) != len(selected_tx):
        raise ValueError("duplicate TXIDs")
    outs: dict[tuple[str, int], Output] = {}
    for o in outputs:
        if o.txid not in tx:
            continue
        key = (o.txid, o.vout)
        if key in outs:
            raise ValueError(f"duplicate outpoint: {key}")
        outs[key] = o
    ins: dict[tuple[str, int], Input] = {}
    for i in inputs:
        if i.txid not in tx:
            continue
        key = (i.txid, i.vin)
        if key in ins:
            raise ValueError(f"duplicate vin: {key}")
        ins[key] = i
    valid_wire = tuple(
        w for w in wire if w.available_at <= cutoff and w.event_time <= cutoff
    )
    edges: list[Edge] = []
    spent: set[tuple[str, int]] = set()
    incoming: dict[str, int] = defaultdict(int)
    missing: set[str] = set()
    for (tid, vin), i in sorted(ins.items()):
        child = tx[tid]
        if child.coinbase:
            raise ValueError("coinbase transaction cannot have previous spend inputs")
        outpoint = (i.prev_txid, i.prev_vout)
        if outpoint in spent:
            raise ValueError(f"double spend in selected evidence snapshot: {outpoint}")
        spent.add(outpoint)
        old = outs.get(outpoint)
        if old is None:
            missing.add(tid)
            continue
        parent = tx[i.prev_txid]
        if parent.event_time > child.event_time or parent.available_at > child.available_at:
            raise ValueError("noncausal referenced prevout")
        incoming[tid] += old.value_sats
        edges.append(Edge(
            edge_id=evidence_id("spend", tid, vin, i.prev_txid, i.prev_vout),
            source="tx:" + i.prev_txid, target="tx:" + tid, relation="spends_outpoint",
            event_time=child.event_time, available_at=child.available_at,
            amount_sats=old.value_sats, source_id=i.source_id,
            evidence_ref=f"input:{tid}:{vin}:{i.prev_txid}:{i.prev_vout}",
        ))
    outtotal: dict[str, int] = defaultdict(int)
    for (_, _), o in sorted(outs.items()):
        outtotal[o.txid] += o.value_sats
        if o.address:
            parent = tx[o.txid]
            edges.append(Edge(
                edge_id=evidence_id("fund", o.txid, o.vout),
                source="tx:" + o.txid, target="addr:" + o.address,
                relation="funds_address", event_time=parent.event_time,
                available_at=parent.available_at, source_id=o.source_id,
                evidence_ref=f"output:{o.txid}:{o.vout}", amount_sats=o.value_sats,
            ))
    for tid, child in tx.items():
        if child.coinbase or tid in missing:
            continue
        if tid not in incoming:
            # Parent not in file: fee and lineage remain UNKNOWN; cannot conserve.
            continue
        if child.fee_sats is not None and incoming[tid] != outtotal[tid] + child.fee_sats:
            raise ValueError(f"known UTXO fee/value conservation failure: {tid}")
    # Dedupe exact copies per sensor/host/txid/time; retain distinct relays.
    seen: set[tuple[str, str, str | None, datetime]] = set()
    joined = 0
    eligible: list[WireObservation] = []
    for w in sorted(valid_wire, key=lambda q: (q.event_time, q.observation_id)):
        key = (w.sensor_id, w.host, w.txid, w.event_time)
        if key in seen:
            continue
        seen.add(key)
        eligible.append(w)
        if w.txid is None or w.txid not in tx or w.decode_provenance == "none":
            continue
        joined += 1
        edges.append(Edge(
            edge_id=evidence_id("wire", w.observation_id),
            source="host:" + w.host, target="tx:" + w.txid,
            relation="observed_relay", event_time=w.event_time,
            available_at=w.available_at, source_id=w.source_id,
            evidence_ref="observation:" + w.observation_id,
        ))
        if w.asn is not None:
            edges.append(Edge(
                edge_id=evidence_id("asn", w.observation_id), source="host:" + w.host,
                target="asn:" + str(w.asn), relation="hosted_in",
                event_time=w.event_time, available_at=w.available_at,
                source_id=w.source_id, evidence_ref="observation:" + w.observation_id,
            ))
            if w.country:
                edges.append(Edge(
                    edge_id=evidence_id("country", w.observation_id),
                    source="asn:" + str(w.asn), target="country:" + w.country,
                    relation="located_in", event_time=w.event_time, available_at=w.available_at,
                    source_id=w.source_id, evidence_ref="observation:" + w.observation_id,
                ))
    coverage = joined / len(eligible) if eligible else 0.0
    sensor_count = len({w.sensor_id for w in eligible if w.txid in tx and w.decode_provenance != "none"})
    reasons: list[str] = []
    mode = Mode.CHAIN_ONLY
    if min_join_coverage is None or max_clock_uncertainty_ms is None:
        reasons.append("cross-layer gates unconfigured; default chain only")
    elif coverage < min_join_coverage or sensor_count < 2:
        reasons.append("insufficient independent exact-TXID join coverage")
    elif any(w.clock_uncertainty_ms > max_clock_uncertainty_ms for w in eligible):
        reasons.append("sensor clock uncertainty exceeds configured threshold")
    else:
        mode = Mode.CROSS_LAYER_ELIGIBLE
        reasons.append("coverage eligible, but independent dependence test still required for Delta")
    if not labels_available:
        reasons.append("no time-eligible credible labels; unsupervised-only modeling")
    if missing:
        reasons.append(f"{len(missing)} transactions have unresolved prevouts")
    return Snapshot(
        cutoff=cutoff, transactions=tuple(tx.values()), inputs=tuple(ins.values()),
        outputs=tuple(outs.values()), wire=tuple(eligible), edges=tuple(edges),
        source_hashes=source_hashes or {},
        readiness=Readiness(mode=mode, labeled=labels_available,
                            wire_join_coverage=coverage, independent_sensors=sensor_count,
                            reasons=tuple(reasons)),
    )


def feature_rows(snapshot: Snapshot) -> list[dict[str, object]]:
    """Causal fixed-width tabular features; excludes labels, identifiers, future data."""
    txs = {tx.txid: tx for tx in snapshot.transactions}
    own_outs: dict[str, list[Output]] = defaultdict(list)
    own_ins: dict[str, list[Input]] = defaultdict(list)
    children: dict[str, list[Edge]] = defaultdict(list)
    for out in snapshot.outputs:
        own_outs[out.txid].append(out)
    for inp in snapshot.inputs:
        own_ins[inp.txid].append(inp)
    for edge in snapshot.edges:
        if edge.relation == "spends_outpoint":
            children[edge.target.removeprefix("tx:")].append(edge)
    rows = []
    for tid, tx in sorted(txs.items(), key=lambda pair: (pair[1].available_at, pair[0])):
        if tx.coinbase:
            continue
        vals = [o.value_sats for o in own_outs[tid]]
        total = sum(vals)
        parents = children[tid]
        age = min(
            (tx.event_time - txs[p.source[3:]].event_time).total_seconds()
            for p in parents
        ) if parents else None
        rows.append({
            "subject_id": tid, "subject_type": "transaction",
            "event_time": tx.event_time.isoformat(), "available_at": tx.available_at.isoformat(),
            "inputs": len(own_ins[tid]), "outputs": len(vals),
            "output_sats": total, "fee_rate": (
                tx.fee_sats / tx.vbytes if tx.fee_sats is not None and tx.vbytes else None
            ), "largest_output_share": max(vals) / total if total else None,
            "min_output_share": min(vals) / total if total else None,
            "age_seconds": age, "unresolved_prevout": bool(own_ins[tid]) and not parents,
            "outgoing_value_sats": total, "source_id": tx.source_id,
        })
    return rows


def graph_export(snapshot: Snapshot, limit: int = 50_000) -> dict[str, object]:
    if len(snapshot.edges) > limit:
        raise ValueError("graph exceeds bounded export limit")
    vertices: dict[str, dict[str, str]] = {}
    for edge in snapshot.edges:
        for node in (edge.source, edge.target):
            kind, _, label = node.partition(":")
            vertices[node] = {"id": node, "type": kind, "label": label[:20]}
    return {
        "cutoff": snapshot.cutoff.isoformat(),
        "nodes": sorted(vertices.values(), key=lambda item: item["id"]),
        "edges": [e.model_dump(mode="json") for e in snapshot.edges],
        "security_note": "observed relays never infer wallet ownership",
    }
