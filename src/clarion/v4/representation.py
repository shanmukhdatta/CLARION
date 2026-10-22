"""Snapshot-safe sparse PyTorch Geometric adapters and temporal graph encoders.

Do not create training representations from an unfiltered future graph.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any

from clarion.v4.contracts import Snapshot, utc

NODE_TYPES = ("tx", "addr", "entity", "host", "asn", "country")


def sparse_hetero_data(snapshot: Snapshot, *, cutoff: datetime | None = None) -> tuple[Any, dict[str, list[str]]]:
    """HeteroData with observed edge types, ID index maps and availability masks.

    Country nodes remain CONTEXT ONLY; graph layers must not use them as
    monetary taint conduits. Use external time-window train masks for targets.
    """
    import torch
    from torch_geometric.data import HeteroData

    effective = utc(cutoff) if cutoff else snapshot.cutoff
    if effective > snapshot.cutoff:
        raise ValueError("cannot expand beyond authorized snapshot cutoff")
    events = [e for e in snapshot.edges if e.available_at <= effective and e.event_time <= effective]
    names: dict[str, set[str]] = {t:set() for t in NODE_TYPES}
    for edge in events:
        for end in (edge.source, edge.target):
            kind, _, identifier = end.partition(":")
            if kind not in names:
                raise ValueError("unknown node type")
            names[kind].add(identifier)
    indices = {k: sorted(ids) for k, ids in names.items()}
    map_indices = {k:{identifier:i for i,identifier in enumerate(arr)} for k, arr in indices.items()}
    graph = HeteroData()
    for kind, names_ in indices.items():
        if not names_:
            continue
        # Only node-type one-hot plus logged observed degree; no TXID lexical embedding.
        graph[kind].x = torch.ones((len(names_), 1), dtype=torch.float32)
        graph[kind].num_nodes = len(names_)
    relations: dict[tuple[str,str,str], list[tuple[int,int,int]]] = defaultdict(list)
    for edge in events:
        source_type, _, source_id = edge.source.partition(":")
        target_type, _, target_id = edge.target.partition(":")
        rel = (source_type, edge.relation, target_type)
        moment = int(edge.available_at.timestamp())
        relations[rel].append((map_indices[source_type][source_id], map_indices[target_type][target_id], moment))
    for rel, pairs in relations.items():
        graph[rel].edge_index = torch.tensor([[a,b] for a,b,_ in pairs], dtype=torch.long).T.contiguous()
        graph[rel].edge_time = torch.tensor([t for _,_,t in pairs],dtype=torch.long)
    graph.cutoff_unix = int(effective.timestamp())
    return graph, indices


def graph_neighbor_statistics(snapshot: Snapshot) -> dict[str, dict[str, float]]:
    """CPU-friendly feature baseline for every node; no identity assumptions."""
    incoming: dict[str, int] = defaultdict(int)
    outgoing: dict[str, int] = defaultdict(int)
    monetary: dict[str, int] = defaultdict(int)
    for edge in snapshot.edges:
        incoming[edge.target] += 1
        outgoing[edge.source] += 1
        if edge.relation == "spends_outpoint" and edge.amount_sats is not None:
            monetary[edge.target] += edge.amount_sats
    all_nodes = sorted(set(incoming) | set(outgoing))
    return {n:{"in_degree":float(incoming[n]),"out_degree":float(outgoing[n]),
               "observed_incoming_sats":float(monetary[n])} for n in all_nodes}


def temporal_hetero_forward(
    hetero_data: Any, *, hidden_dim: int = 32,
    seed: int = 26,
) -> dict[str, Any]:
    """Untrained temporal hetero-GNN *forward pass* for interface checks only.

    Training requires vetted fold-specific objectives and labels. Neither the
    neural outputs nor attention weights prove identity or criminal activity.
    """
    import torch
    from torch import nn
    from torch_geometric.nn import HeteroConv, SAGEConv

    torch.manual_seed(seed)
    graph = hetero_data
    x_dict = graph.x_dict
    if not x_dict or not graph.edge_types:
        raise ValueError("nonempty typed graph required")
    # Country edges intentionally omitted to avoid political/geographic risk learning.
    relations = [edge for edge in graph.edge_types if "country" not in (edge[0],edge[2])]
    if not relations:
        raise ValueError("no eligible message passing edges")

    class Block(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.projectors = nn.ModuleDict({
                name: nn.Linear(tensor.shape[-1], hidden_dim)
                for name, tensor in x_dict.items()
            })
            self.conv = HeteroConv({
                relation: SAGEConv((-1,-1),hidden_dim)
                for relation in relations
            }, aggr="sum")

        def forward(self) -> dict[str, Any]:
            x = {kind:layer(x_dict[kind]).relu()
                 for kind,layer in self.projectors.items()}
            message = self.conv(x, {
                relation: graph[relation].edge_index for relation in relations
            })
            return {k: message.get(k,x[k]) for k in x}

    block=Block()
    block.eval()
    with torch.no_grad():
        return {k:v.detach().cpu().numpy() for k,v in block().items()}


def assert_cutoff(snapshot: Snapshot, max_time: datetime) -> None:
    cutoff = utc(max_time)
    for edge in snapshot.edges:
        if edge.available_at > cutoff or edge.event_time > cutoff:
            raise ValueError(f"future edge present: {edge.edge_id}")
