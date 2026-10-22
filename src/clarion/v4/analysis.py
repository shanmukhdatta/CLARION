"""MCER candidates, explanatory motifs, frozen two-pass risk propagation."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from math import exp

from clarion.v4.contracts import Snapshot, evidence_id


@dataclass(frozen=True)
class EntityCandidate:
    entity_id: str
    members: tuple[str, ...]
    support: tuple[str, ...]
    status: str = "TENTATIVE_COMMON_INPUT"


def mcer_candidates(
    snapshot: Snapshot, *, disputed_txids: set[str] | None = None,
    service_addresses: set[str] | None = None,
) -> list[EntityCandidate]:
    """Only evidence-carrying H1 common-input proposals; no automatic wire merges.

    H2-H5 need data-specific calibrated evidence and therefore DO NOT automatically
    affect group membership. CoinJoin/service exclusions are hard stop barriers.
    """
    disputed_txids = disputed_txids or set()
    service_addresses = service_addresses or set()
    outpoints = {(o.txid, o.vout): o for o in snapshot.outputs}
    tx_in: dict[str, list[object]] = defaultdict(list)
    for i in snapshot.inputs:
        tx_in[i.txid].append(i)
    proposals: list[tuple[str, str, str]] = []
    for tid, inputs in tx_in.items():
        if tid in disputed_txids or len(inputs) < 2:
            continue
        addresses = []
        for i in inputs:
            out = outpoints.get((i.prev_txid, i.prev_vout))
            if out is not None and out.address and out.address not in service_addresses:
                addresses.append(out.address)
        # Multi-party equal-input value pattern: abstain conservatively
        values = [outpoints[(i.prev_txid, i.prev_vout)].value_sats for i in inputs if (i.prev_txid, i.prev_vout) in outpoints]
        if len(values) >= 3 and len(set(values)) == 1:
            continue
        addresses = sorted(set(addresses))
        for j, left in enumerate(addresses):
            for right in addresses[j + 1:]:
                proposals.append((left, right, tid))
    adjacency: dict[str, set[str]] = defaultdict(set)
    support: dict[frozenset[str], list[str]] = defaultdict(list)
    for a, b, tid in proposals:
        adjacency[a].add(b)
        adjacency[b].add(a)
        support[frozenset((a, b))].append("H1:common-input:" + tid)
    seen = set()
    result = []
    for first in sorted(adjacency):
        if first in seen:
            continue
        stack, members, proofs = [first], set(), set()
        while stack:
            cur = stack.pop()
            if cur in members:
                continue
            members.add(cur)
            for peer in adjacency[cur]:
                proofs.update(support[frozenset((cur, peer))])
                if peer not in members:
                    stack.append(peer)
        seen.update(members)
        if len(members) > 1:
            ordered = tuple(sorted(members))
            result.append(EntityCandidate(
                entity_id="entity:" + evidence_id(*ordered),
                members=ordered, support=tuple(sorted(proofs)),
            ))
    return result


def pattern_candidates(snapshot: Snapshot) -> list[dict[str, object]]:
    """Conservative peel, CoinJoin-like and burst/layering candidates with witnesses."""
    by_tx = {t.txid: t for t in snapshot.transactions}
    outs: dict[str, list[int]] = defaultdict(list)
    for o in snapshot.outputs:
        outs[o.txid].append(o.value_sats)
    incoming: dict[str, list[str]] = defaultdict(list)
    outgoing: dict[str, list[str]] = defaultdict(list)
    for edge in snapshot.edges:
        if edge.relation == "spends_outpoint":
            parent, child = edge.source[3:], edge.target[3:]
            incoming[child].append(parent)
            outgoing[parent].append(child)
    patterns = []
    for txid, tx in by_tx.items():
        amounts = outs.get(txid, [])
        if len(amounts) >= 5:
            repeats = len(amounts) - len(set(amounts))
            if repeats >= 2:
                patterns.append({
                    "id": evidence_id("mix", txid), "kind": "coinjoin_like",
                    "subject_id": txid, "witness_txids": [txid],
                    "evidence_refs": [f"output:{txid}"],
                    "benign_alternative": "privacy or service batching",
                    "uncertainty": "cannot identify participants",
                })
        if len(incoming[txid]) >= 4 or len(outgoing[txid]) >= 4:
            patterns.append({
                "id": evidence_id("layer", txid), "kind": "fan_in_out",
                "subject_id": txid, "witness_txids": sorted(set(incoming[txid] + [txid] + outgoing[txid])),
                "evidence_refs": [f"input:{txid}"],
                "benign_alternative": "exchange consolidation or processor batching",
                "uncertainty": "structure does not prove laundering",
            })
        path = [txid]
        while len(path) < 3 and len(incoming[path[-1]]) == 1:
            prev = incoming[path[-1]][0]
            if prev in path:
                break
            path.append(prev)
        if len(path) != 3:
            continue
        path.reverse()
        if any(len(outs.get(node, [])) < 2 or not (0.76 <= max(outs[node]) / max(sum(outs[node]), 1) <= 0.995) for node in path):
            continue
        if any(by_tx[path[j]].event_time > by_tx[path[j + 1]].event_time for j in range(2)):
            continue
        patterns.append({
            "id": evidence_id("peel", *path), "kind": "peel_like",
            "subject_id": txid, "witness_txids": path,
            "evidence_refs": [f"transaction:{x}" for x in path],
            "benign_alternative": "normal wallet change or merchant split",
            "uncertainty": "heuristic structural lead only",
        })
    return patterns


def local_priority(
    subject_id: str, *, supervised_score: float | None,
    anomaly_rank: float | None, motif_count: int, delta: float | None,
    pi: float | None, label_validated: bool = False,
) -> dict[str, object]:
    """Explicit 0..75 provisional lead points; NEVER calibrated guilt probability.

    Δ/Π are omitted, not silently treated as zero; weights illustrative.
    """
    if supervised_score is not None and not label_validated:
        raise ValueError("supervised score needs validated subject-level labels")
    terms = {
        "supervised": 35.0 * supervised_score if supervised_score is not None else None,
        "novelty": 20.0 * anomaly_rank if anomaly_rank is not None else None,
        "motif": min(20.0, motif_count * 6.0),
        "delta": 0.0 if delta is None else 8.0 * delta,
        "pi": 0.0 if pi is None else 5.0 * pi,
    }
    result = min(75.0, max(0.0, sum(v for v in terms.values() if v is not None)))
    return {
        "subject_id": subject_id, "local_points": round(result, 3),
        "terms": terms, "delta_status": "ABSTAIN" if delta is None else "ELIGIBLE",
        "pi_status": "ABSTAIN" if pi is None else "ELIGIBLE",
        "score_type": "heuristic_priority_not_crime_probability",
    }


def propagate(
    snapshot: Snapshot, frozen_local: dict[str, float], *,
    max_hops: int = 6, damping: float = 0.42,
    blocked_transactions: set[str] | None = None,
) -> dict[str, object]:
    """Financial forward exposure only; never relay/ASN/Country propagation.

    Compute exclusively from immutable seeds and time-valid verified outpoints.
    Return bounded pass-2 PRIOR: min(25, exposure*25/75).
    """
    if not (1 <= max_hops <= 6) or not (0.0 < damping < 1.0):
        raise ValueError("invalid propagation controls")
    blocked_transactions = blocked_transactions or set()
    adjacency: dict[str, list[tuple[str, float, datetime]]] = defaultdict(list)
    for edge in snapshot.edges:
        if edge.relation != "spends_outpoint":
            continue
        src, dest = edge.source[3:], edge.target[3:]
        if src in blocked_transactions or dest in blocked_transactions:
            continue
        adjacency[src].append((dest, float(edge.amount_sats or 0), edge.event_time))
    # Bound outgoing allocated fractions per source by observed sum (<=1).
    totals = {src: sum(v for _, v, _ in arr) for src, arr in adjacency.items()}
    exposure: dict[str, float] = defaultdict(float)
    witness: dict[str, list[str]] = {}
    for source, base in sorted(frozen_local.items()):
        if source in blocked_transactions or base <= 0:
            continue
        frontier = [(source, min(75.0, base), [source], None)]
        for hop in range(1, max_hops + 1):
            future = []
            for current, mass, path, last_time in frontier:
                for dest, amount, stamp in adjacency[current]:
                    if dest in path or (last_time is not None and stamp < last_time):
                        continue
                    fraction = amount / totals[current] if totals[current] else 0.0
                    attenuated = mass * damping * fraction * exp(-0.10 * (hop - 1))
                    if attenuated < 0.001:
                        continue
                    exposure[dest] += attenuated
                    new_path = path + [dest]
                    if dest not in witness or attenuated > (exposure[dest] - attenuated):
                        witness[dest] = new_path
                    future.append((dest, attenuated, new_path, stamp))
            frontier = future[:10_000]
            if not frontier:
                break
    prior = {tid: round(min(25.0, 25.0 * value / 75.0), 3) for tid, value in exposure.items()}
    return {
        "frozen_seed_hash": evidence_id(*sorted(f"{tid}:{s}" for tid, s in frozen_local.items())),
        "propagation_prior": prior, "top_paths": witness, "max_hops": max_hops,
        "note": "exposure signal, not guilt or ownership",
    }


def final_priority(local_points: float, propagation_prior: float) -> float:
    if not 0 <= local_points <= 75 or not 0 <= propagation_prior <= 25:
        raise ValueError("pass 1 must be <=75 and propagation must be <=25")
    return round(min(100.0, local_points + propagation_prior), 3)
