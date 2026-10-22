"""Temporal, group-safe supervised and unsupervised baselines with optional GNN.

No object unpickling; prediction files hold scores + manifest only. Artifacts from
synthetic labels MUST NOT be deployed as calibrated real-world criminality predictions.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from typing import Any, Sequence


FEATURES = (
    "inputs", "outputs", "output_sats", "fee_rate",
    "largest_output_share", "min_output_share", "age_seconds",
    "unresolved_prevout",
)


@dataclass(frozen=True)
class TrainReport:
    status: str
    feature_names: tuple[str, ...]
    train_count: int
    future_count: int
    meta_oof_count: int
    holdout: dict[str, float]
    predictions: list[dict[str, object]]
    caveats: tuple[str, ...]


def _xy(rows: Sequence[dict[str, object]]) -> Any:
    import numpy as np
    return np.array([
        [float(row[k]) if row.get(k) is not None else float("nan") for k in FEATURES]
        for row in rows
    ], dtype=float)


def fit_temporal_stack(
    feature_rows: Sequence[dict[str, object]], labels: dict[str, tuple[int, str]],
    *, groups: dict[str, str] | None = None,
    seed: int = 26, holdout_share: float = 0.20, folds: int = 4,
) -> TrainReport:
    """OOF by chronological independent groups and final untouched future holdout.

    labels maps subject_id -> (0|1, ISO8601 available_at). Missing or delayed
    labels are excluded; group collisions across train/holdout are forbidden.
    Graph snapshots/embeddings must be separately recomputed per fold upstream.
    """
    import numpy as np
    from sklearn.ensemble import IsolationForest, RandomForestClassifier
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import average_precision_score, roc_auc_score
    from sklearn.model_selection import TimeSeriesSplit
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    if not (0.1 <= holdout_share <= 0.4) or folds < 2:
        raise ValueError("invalid split or fold controls")
    ordered = sorted(feature_rows, key=lambda r: (str(r["available_at"]), str(r["subject_id"])))
    eligible = [
        r for r in ordered if str(r["subject_id"]) in labels
        and labels[str(r["subject_id"])][1] <= str(r["available_at"])
    ]
    if len(eligible) < 50:
        raise ValueError("at least 50 temporally eligible labeled rows required")
    # Group by explicitly supplied temporal-independent case, default each tx.
    group_map = groups or {}
    grouped: dict[str, list[dict[str, object]]] = {}
    for r in eligible:
        gid = group_map.get(str(r["subject_id"]), str(r["subject_id"]))
        grouped.setdefault(gid, []).append(r)
    ordered_groups = sorted(grouped, key=lambda gid: min(str(r["available_at"]) for r in grouped[gid]))
    cut = int((1 - holdout_share) * len(ordered_groups))
    if cut <= folds * 2 or cut >= len(ordered_groups):
        raise ValueError("too few independent temporal groups")
    historical = [r for gid in ordered_groups[:cut] for r in grouped[gid]]
    future = [r for gid in ordered_groups[cut:] for r in grouped[gid]]
    if max(str(r["available_at"]) for r in historical) >= min(str(r["available_at"]) for r in future):
        raise ValueError("overlapping group windows; must purge boundary groups")
    y = np.array([labels[str(r["subject_id"])][0] for r in historical], dtype=int)
    y_future = np.array([labels[str(r["subject_id"])][0] for r in future], dtype=int)
    if set(y) != {0, 1}:
        raise ValueError("historical window missing a class")
    X, Xfuture = _xy(historical), _xy(future)

    def learner(kind: str) -> Any:
        if kind == "logistic":
            return make_pipeline(
                SimpleImputer(strategy="median", add_indicator=True), StandardScaler(),
                LogisticRegression(max_iter=700, random_state=seed),
            )
        return make_pipeline(
            SimpleImputer(strategy="median", add_indicator=True),
            RandomForestClassifier(n_estimators=180, min_samples_leaf=3,
                                   random_state=seed, n_jobs=1),
        )

    def novel() -> Any:
        return make_pipeline(
            SimpleImputer(strategy="median", add_indicator=True),
            IsolationForest(n_estimators=100, random_state=seed, contamination="auto"),
        )

    oof = np.full((len(historical), 3), np.nan, dtype=float)
    index = {id(r): idx for idx, r in enumerate(historical)}
    splitter = TimeSeriesSplit(n_splits=folds)
    for past_group_idx, valid_group_idx in splitter.split(ordered_groups[:cut]):
        before = {ordered_groups[i] for i in past_group_idx}
        after = {ordered_groups[i] for i in valid_group_idx}
        prev = [index[id(r)] for gid in before for r in grouped[gid]]
        curr = [index[id(r)] for gid in after for r in grouped[gid]]
        if set(y[prev]) != {0, 1}:
            continue
        models = [learner("logistic"), learner("forest")]
        for model in models:
            model.fit(X[prev], y[prev])
        detector = novel().fit(X[prev])
        oof[curr, 0] = models[0].predict_proba(X[curr])[:, 1]
        oof[curr, 1] = models[1].predict_proba(X[curr])[:, 1]
        oof[curr, 2] = -detector.decision_function(X[curr])
    usable = np.isfinite(oof).all(axis=1)
    if usable.sum() < 20 or set(y[usable]) != {0, 1}:
        raise ValueError("not enough eligible OOF fold predictions")
    meta = make_pipeline(StandardScaler(), LogisticRegression(max_iter=700, random_state=seed))
    meta.fit(oof[usable], y[usable])
    bases = [learner("logistic"), learner("forest")]
    for model in bases:
        model.fit(X, y)
    detector = novel().fit(X)
    future_meta = np.column_stack([
        bases[0].predict_proba(Xfuture)[:, 1],
        bases[1].predict_proba(Xfuture)[:, 1],
        -detector.decision_function(Xfuture),
    ])
    scores = meta.predict_proba(future_meta)[:, 1]
    metrics = {}
    if len(set(y_future)) == 2:
        metrics = {"auroc": round(float(roc_auc_score(y_future, scores)), 5),
                   "auprc": round(float(average_precision_score(y_future, scores)), 5)}
    preds = [
        {"subject_id": str(r["subject_id"]), "score": round(float(s), 6),
         "kind": "SUPERVISED_UNCALIBRATED", "split": "future_holdout"}
        for r, s in zip(future, scores, strict=True)
    ]
    return TrainReport(
        status="EXPERIMENTAL_UNCALIBRATED", feature_names=FEATURES,
        train_count=len(historical), future_count=len(future),
        meta_oof_count=int(usable.sum()), holdout=metrics, predictions=preds,
        caveats=(
            "Synthetic benchmark labels do not validate real-world AML performance",
            "No independent calibration split or conformal coverage established",
            "GNN embeddings MUST be recomputed inside each training fold, never globally",
        ),
    )


def novelty_ranking(rows: Sequence[dict[str, object]], *, seed: int = 26) -> list[dict[str, object]]:
    """Unsupervised novelty RANK only; never probability of illicit activity."""
    if len(rows) < 10:
        raise ValueError("novelty fitting requires >=10 rows")
    import numpy as np
    from sklearn.ensemble import IsolationForest
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import make_pipeline

    matrix = _xy(rows)
    model = make_pipeline(SimpleImputer(strategy="median", add_indicator=True),
                          IsolationForest(n_estimators=150, contamination="auto", random_state=seed))
    scores = -model.fit(matrix).decision_function(matrix)
    order = np.argsort(np.argsort(scores, kind="stable"), kind="stable")
    ranked = order / max(1, len(rows) - 1)
    return [
        {"subject_id": str(row["subject_id"]), "novelty_rank": round(float(rank), 6),
         "kind": "UNSUPERVISED_RANK_NOT_PROBABILITY"}
        for row, rank in zip(rows, ranked, strict=True)
    ]


def optional_pyg_encoder(
    x: Any, edge_index: Any, *, model_kind: str = "sage",
    out_channels: int = 32, epochs: int = 30, seed: int = 26,
) -> Any:
    """Optional CPU PyTorch Geometric GraphSAGE/GAT unsupervised edge reconstruction.

    This is a challenger embedding only, not an evidence or ownership classifier.
    Does not fetch pretrained weights and does not introduce future snapshot edges.
    """
    import torch
    from torch import nn
    from torch_geometric.nn import GATConv, SAGEConv

    if model_kind not in ("sage", "gat"):
        raise ValueError("model_kind must be sage or gat")
    torch.manual_seed(seed)
    x = torch.as_tensor(x, dtype=torch.float32)
    edge_index = torch.as_tensor(edge_index, dtype=torch.long)
    if edge_index.ndim != 2 or edge_index.shape[0] != 2 or x.shape[0] < 2:
        raise ValueError("invalid graph tensor contract")

    class Encoder(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            conv = SAGEConv if model_kind == "sage" else GATConv
            self.first = conv(x.shape[1], 64)
            self.second = conv(64, out_channels)

        def forward(self, features: Any, edges: Any) -> Any:
            return self.second(torch.relu(self.first(features, edges)), edges)

    model = Encoder()
    opt = torch.optim.Adam(model.parameters(), lr=0.005)
    for _ in range(epochs):
        model.train()
        opt.zero_grad()
        z = model(x, edge_index)
        positive = (z[edge_index[0]] * z[edge_index[1]]).sum(dim=1)
        # Negative sampling is edge reconstruction task only.
        rand_a = torch.randint(x.shape[0], positive.shape, dtype=torch.long)
        rand_b = torch.randint(x.shape[0], positive.shape, dtype=torch.long)
        negative = (z[rand_a] * z[rand_b]).sum(dim=1)
        loss = torch.nn.functional.softplus(-positive).mean() + torch.nn.functional.softplus(negative).mean()
        loss.backward()
        opt.step()
    model.eval()
    with torch.no_grad():
        return model(x, edge_index).numpy()
