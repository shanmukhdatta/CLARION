"""Optional CPU GraphSAGE self-supervised edge reconstruction and safe JSON inference.

Research proxy only. Non-edges are UNKNOWN, not proven benign or illicit.
No pickle loading, no source IP attribution, no future-edge message passing.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from datetime import datetime
from pathlib import Path
from typing import Any


def prepare_graph(graph_file: str | Path, *, cutoff: str | None = None) -> dict[str, Any]:
    path = Path(graph_file)
    if path.stat().st_size > 20_000_000:
        raise ValueError("large graphs require neighbor-sampled research training")
    raw = path.read_bytes()
    graph = json.loads(raw)
    end = datetime.fromisoformat(cutoff.replace("Z", "+00:00")) if cutoff else None
    spend = []
    for row in graph.get("edges", []):
        if row.get("relation") != "spends_outpoint":
            continue
        timestamp = datetime.fromisoformat(row["available_at"].replace("Z", "+00:00"))
        if end is None or timestamp <= end:
            spend.append((str(row["source"]), str(row["target"]), timestamp.isoformat()))
    spend.sort(key=lambda x: (x[2], x[0], x[1]))
    names = sorted({name for edge in spend for name in edge[:2]})
    if len(names) < 3 or len(names) > 800 or len(spend) > 3000:
        raise ValueError("demo GraphSAGE requires 3..800 nodes and <=3000 observed spend edges")
    index = {name: i for i, name in enumerate(names)}
    return {
        "index": index, "ordered_edges": [(index[a], index[b]) for a, b, _ in spend],
        "nodes": names, "graph_sha256": hashlib.sha256(raw).hexdigest(),
        "cutoff": cutoff or graph.get("cutoff"), "observed_count": len(spend),
    }


def _make_model(torch: Any, SAGEConv: Any, hidden: int = 16) -> Any:
    from torch import nn

    class Reconstructor(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.first = SAGEConv(2, hidden)
            self.second = SAGEConv(hidden, hidden)

        def forward(self, x: Any, edge_index: Any) -> Any:
            return self.second(self.first(x, edge_index).relu(), edge_index)

    return Reconstructor()


def _tensors(torch: Any, info: dict[str, Any], train_edges: list[tuple[int, int]]) -> tuple[Any, Any]:
    n = len(info["nodes"])
    indegree, outdegree = [0.0] * n, [0.0] * n
    for a, b in train_edges:
        outdegree[a] += 1
        indegree[b] += 1
    x = torch.tensor(
        [[math.log1p(indegree[i]), math.log1p(outdegree[i])] for i in range(n)],
        dtype=torch.float32,
    )
    e = torch.tensor(train_edges, dtype=torch.long).t().contiguous()
    if e.numel() == 0:
        raise ValueError("no training edges")
    return x, e


def train_graphsage(
    graph_file: str | Path, output: str | Path, *,
    cutoff: str | None = None, epochs: int = 12, seed: int = 26
) -> dict[str, Any]:
    """Fit on earliest 80% of observed edges; save portable bounded JSON weights."""
    if not 1 <= epochs <= 100:
        raise ValueError("epochs out of bounds")
    info = prepare_graph(graph_file, cutoff=cutoff)
    import torch
    from torch_geometric.nn import SAGEConv

    torch.manual_seed(seed)
    random.seed(seed)
    edges = info["ordered_edges"]
    split = max(1, int(0.8 * len(edges)))
    if split >= len(edges):
        raise ValueError("need separate chronological edges for a holdout")
    train_edges, holdout = edges[:split], edges[split:]
    x, e = _tensors(torch, info, train_edges)
    model = _make_model(torch, SAGEConv)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    rng = random.Random(seed)  # noqa: S311 - deterministic research sampling, not cryptography
    observed = set(edges)
    possible = [(a, b) for a in range(len(info["nodes"]))
                for b in range(len(info["nodes"])) if a != b and (a, b) not in observed]
    if not possible:
        raise ValueError("no unobserved candidate edges for proxy negatives")
    for _ in range(epochs):
        model.train()
        optimizer.zero_grad()
        z = model(x, e)
        pos = torch.tensor(train_edges, dtype=torch.long)
        negatives = [possible[rng.randrange(len(possible))] for _ in train_edges]
        neg = torch.tensor(negatives, dtype=torch.long)
        pos_logits = (z[pos[:, 0]] * z[pos[:, 1]]).sum(dim=1)
        neg_logits = (z[neg[:, 0]] * z[neg[:, 1]]).sum(dim=1)
        loss = (
            torch.nn.functional.softplus(-pos_logits).mean()
            + torch.nn.functional.softplus(neg_logits).mean()
        )
        loss.backward()
        optimizer.step()
    model.eval()
    with torch.no_grad():
        embeddings = model(x, e)
        test_scores = [float(torch.sigmoid((embeddings[a] * embeddings[b]).sum()))
                       for a, b in holdout]
    artifact = {
        "schema_version": 1, "model_type": "GRAPH_SAGE_EDGE_RECONSTRUCTION_PROXY",
        "score_type": "UNSUPERVISED_LINK_SCORE_NOT_ILLICIT_PROBABILITY",
        "graph_sha256": info["graph_sha256"], "cutoff": info["cutoff"],
        "nodes": info["nodes"], "train_edges": train_edges,
        "training_edges": len(train_edges), "future_edges": len(holdout),
        "feature_names": ["past_in_degree_log1p", "past_out_degree_log1p"],
        "seed": seed, "epochs": epochs, "hidden": 16,
        "state_dict": {k: v.detach().cpu().tolist() for k, v in model.state_dict().items()},
        "future_positive_proxy_mean": sum(test_scores) / len(test_scores),
        "limitations": ["future edges are observed positives; unobserved pairs are not verified negatives",
                        "weights and degree features are graph-snapshot-specific",
                        "no claims about real illicit behavior, wallet identity or classification accuracy"],
    }
    dest = Path(output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(artifact, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return {k: artifact[k] for k in ("model_type", "score_type", "training_edges", "future_edges", "future_positive_proxy_mean")}


def infer_graphsage(
    graph_file: str | Path, model_file: str | Path, source: str, target: str
) -> dict[str, Any]:
    """Infer only on the exact snapshot used to construct train-time features."""
    artifact_path = Path(model_file)
    if artifact_path.stat().st_size > 3_000_000:
        raise ValueError("oversized model JSON")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if artifact.get("schema_version") != 1 or artifact.get("model_type") != "GRAPH_SAGE_EDGE_RECONSTRUCTION_PROXY":
        raise ValueError("unrecognized model contract")
    info = prepare_graph(graph_file, cutoff=artifact["cutoff"])
    if info["graph_sha256"] != artifact["graph_sha256"] or info["nodes"] != artifact["nodes"]:
        raise ValueError("graph/source mismatch: retrain instead of unsafe re-use")
    if source not in info["index"] or target not in info["index"]:
        return {"status": "ABSTAIN_UNKNOWN_NODE"}
    import torch
    from torch_geometric.nn import SAGEConv

    model = _make_model(torch, SAGEConv, int(artifact["hidden"]))
    current = model.state_dict()
    weights = artifact["state_dict"]
    if set(weights) != set(current):
        raise ValueError("weight key mismatch")
    model.load_state_dict({k: torch.tensor(weights[k], dtype=v.dtype)
                           for k, v in current.items()}, strict=True)
    x, edges = _tensors(torch, info, [tuple(x) for x in artifact["train_edges"]])
    model.eval()
    with torch.no_grad():
        z = model(x, edges)
        a, b = info["index"][source], info["index"][target]
        score = float(torch.sigmoid((z[a] * z[b]).sum()))
    return {"status": "EXPERIMENTAL_UNCALIBRATED", "link_proxy_score": round(score, 6),
            "score_type": artifact["score_type"], "model_graph_sha256": artifact["graph_sha256"]}
