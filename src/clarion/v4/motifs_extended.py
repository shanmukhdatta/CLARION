"""Additional explainable Bitcoin flow motifs, with careful address ambiguity.

Transaction-value edges remain a DAG; an address revisited by outputs is not
evidence of a cyclic money transfer or a particular wallet controller.
"""
from __future__ import annotations

from collections import defaultdict

from clarion.v4.contracts import Snapshot, evidence_id


def additional_motifs(snapshot: Snapshot, *, max_hops: int = 5) -> list[dict[str, object]]:
    if not 2 <= max_hops <= 6:
        raise ValueError("max_hops must be 2..6")
    tx_time = {t.txid: t.event_time for t in snapshot.transactions}
    outpoints = {(o.txid, o.vout): o for o in snapshot.outputs}
    address_inputs: dict[str, set[str]] = defaultdict(set)
    output_addresses: dict[str, set[str]] = defaultdict(set)
    children: dict[str, set[str]] = defaultdict(set)
    parents: dict[str, set[str]] = defaultdict(set)
    for o in snapshot.outputs:
        if o.address:
            output_addresses[o.txid].add(o.address)
    for inp in snapshot.inputs:
        parent = outpoints.get((inp.prev_txid, inp.prev_vout))
        if parent and parent.address:
            address_inputs[inp.txid].add(parent.address)
    for edge in snapshot.edges:
        if edge.relation != "spends_outpoint":
            continue
        a, b = edge.source.removeprefix("tx:"), edge.target.removeprefix("tx:")
        children[a].add(b)
        parents[b].add(a)

    found: list[dict[str, object]] = []
    seen: set[tuple[str, ...]] = set()
    # Layered fan-in/fan-out structure: structural lead, not automatically illicit.
    for center in sorted(tx_time):
        incoming = parents[center]
        outgoing = children[center]
        if len(incoming) < 3 or len(outgoing) < 3:
            continue
        witnesses = tuple(sorted(incoming) + [center] + sorted(outgoing))
        if witnesses in seen:
            continue
        seen.add(witnesses)
        found.append({
            "id": evidence_id("layered", *witnesses),
            "kind": "layering_candidate",
            "subject_id": center, "witness_txids": list(witnesses),
            "evidence_refs": [f"transaction:{tid}" for tid in witnesses],
            "benign_alternative": "exchange aggregation or batched payouts",
            "uncertainty": "topological fan-in/out does not prove money laundering",
        })

    # Causal return-to-script-pattern path, NOT a causal graph cycle.
    for origin in sorted(tx_time):
        starters = output_addresses.get(origin, set())
        if not starters:
            continue
        frontier: list[tuple[str, tuple[str, ...]]] = [(origin, (origin,))]
        for _ in range(max_hops):
            next_frontier = []
            for node, path in frontier:
                for dest in sorted(children[node]):
                    if dest in path or tx_time[dest] < tx_time[node]:
                        continue
                    extended = (*path, dest)
                    if len(extended) >= 3 and starters & output_addresses.get(dest, set()):
                        key = extended
                        if key not in seen:
                            found.append({
                                "id": evidence_id("return", *key),
                                "kind": "return_to_script_candidate",
                                "subject_id": dest,
                                "witness_txids": list(extended),
                                "evidence_refs": [f"transaction:{tid}" for tid in extended],
                                "revisited_addresses": sorted(
                                    starters & output_addresses.get(dest, set())
                                ),
                                "benign_alternative": "change address reuse or wallet service routing",
                                "uncertainty": "script reuse is not wallet-controller attribution",
                            })
                            seen.add(key)
                    if len(extended) <= max_hops:
                        next_frontier.append((dest, extended))
            frontier = next_frontier[:5000]
            if not frontier:
                break
    return found[:10000]
