"""GraphSAGE parsing/cutoff tests, independent of heavyweight torch/PyG install."""
from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

import pytest

from clarion.v4.gnn_training import prepare_graph


def _graph(path):
    start = datetime(2025, 1, 1, tzinfo=UTC)
    edges = [{"source": f"tx:{chr(97+i)}", "target": f"tx:{chr(98+i)}",
              "relation": "spends_outpoint",
              "available_at": (start + timedelta(days=i)).isoformat()}
             for i in range(3)]
    edges.append({"source": "host:h", "target": "tx:c",
                  "relation": "observed_relay", "available_at": start.isoformat()})
    path.write_text(json.dumps({"edges": edges, "cutoff": start.isoformat()}))
    return start


def test_gnn_excludes_wire_observation(tmp_path):
    path = tmp_path / "graph.json"
    _graph(path)
    result = prepare_graph(path)
    assert result["observed_count"] == 3
    assert all(node.startswith("tx:") for node in result["nodes"])


def test_gnn_requires_at_least_three_nodes(tmp_path):
    path = tmp_path / "graph.json"
    start = _graph(path)
    with pytest.raises(ValueError, match="3..800 nodes"):
        prepare_graph(path, cutoff=(start + timedelta(hours=1)).isoformat())


def test_gnn_model_inference_never_runs_without_artifact(tmp_path):
    from clarion.v4.submission import model_readiness
    assert model_readiness(tmp_path / "missing.json")["status"] == "MODEL_NOT_CONNECTED"
