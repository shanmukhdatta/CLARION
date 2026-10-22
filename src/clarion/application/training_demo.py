"""Chronological demo-only out-of-fold stacking. NOT validated real-world AML prediction."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, f1_score, roc_auc_score
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from clarion.application.engine import _json, _read, load

FEATURE_NAMES = ["fee_rate", "output_count", "input_count", "largest_output_share", "smallest_output_share", "age_seconds"]


def _matrix(rows: list[dict[str, Any]]) -> np.ndarray:
    return np.asarray([[float(r[c]) for c in FEATURE_NAMES] for r in rows], dtype=float)


def _base(seed: int) -> tuple[Any, Any]:
    return (make_pipeline(StandardScaler(), LogisticRegression(max_iter=400, random_state=seed)),
            RandomForestClassifier(n_estimators=80, max_depth=6, min_samples_leaf=2, random_state=seed, n_jobs=1))


def _score(model: Any, values: np.ndarray) -> np.ndarray:
    return model.predict_proba(values)[:, list(model.classes_).index(1)] if hasattr(model, "classes_") else model.predict_proba(values)[:, 1]


def train(directory: str | Path, output: str | Path, seed: int = 26) -> dict[str, Any]:
    """Fit on independent historical cases; evaluate only future cases.

    Truth is loaded explicitly here (never loaded during ingestion or inference).
    Models are NOT saved via pickle; serialized outputs are analysis-only scores.
    """
    data = load(directory)
    rows = sorted(data["features"], key=lambda x: (x["time"], x["txid"]))
    labels = {r["txid"]: int(r["label"]) for r in _read(Path(directory) / "truth_SYNTHETIC_ONLY.csv")}
    if len(rows) < 75 or any(r["txid"] not in labels for r in rows):
        raise ValueError("requires >=75 properly labeled synthetic spend transactions")
    ordered_cases = list(dict.fromkeys(r["case_id"] for r in rows))
    if len(ordered_cases) < 30:
        raise ValueError("requires >=30 independent cases for temporal demo")
    boundary = int(len(ordered_cases) * .8)
    train_cases, test_cases = set(ordered_cases[:boundary]), set(ordered_cases[boundary:])
    train_rows = [r for r in rows if r["case_id"] in train_cases]
    test_rows = [r for r in rows if r["case_id"] in test_cases]
    X, X_future = _matrix(train_rows), _matrix(test_rows)
    y = np.array([labels[r["txid"]] for r in train_rows])
    y_future = np.array([labels[r["txid"]] for r in test_rows])
    if len(set(y)) < 2 or len(set(y_future)) < 2:
        raise ValueError("demo seed has only one class in temporal train or future holdout")

    # Group OOF by case. Earlier folds may be all one class; leave them out.
    train_case_order = list(dict.fromkeys(r["case_id"] for r in train_rows))
    oof = np.full((len(train_rows), 3), np.nan)
    splitter = TimeSeriesSplit(n_splits=4)
    for c_train, c_valid in splitter.split(train_case_order):
        hist = {train_case_order[i] for i in c_train}
        fut = {train_case_order[i] for i in c_valid}
        in_idx = np.array([i for i, r in enumerate(train_rows) if r["case_id"] in hist], dtype=int)
        va_idx = np.array([i for i, r in enumerate(train_rows) if r["case_id"] in fut], dtype=int)
        if len(set(y[in_idx])) < 2:
            continue
        b1, b2 = _base(seed)
        b1.fit(X[in_idx], y[in_idx])
        b2.fit(X[in_idx], y[in_idx])
        novelty = IsolationForest(n_estimators=80, contamination="auto", random_state=seed).fit(X[in_idx])
        oof[va_idx, 0] = b1.predict_proba(X[va_idx])[:, 1]
        oof[va_idx, 1] = b2.predict_proba(X[va_idx])[:, 1]
        # Outlier novelty is an anomaly ranking feature, not illicit probability.
        oof[va_idx, 2] = -novelty.decision_function(X[va_idx])
    eligible = np.isfinite(oof).all(axis=1)
    if int(eligible.sum()) < 12 or len(set(y[eligible])) < 2:
        raise ValueError("too few eligible out-of-fold predictions; generate more cases")
    meta = make_pipeline(StandardScaler(), LogisticRegression(max_iter=400, random_state=seed))
    meta.fit(oof[eligible], y[eligible])
    b1, b2 = _base(seed)
    b1.fit(X, y)
    b2.fit(X, y)
    novelty = IsolationForest(n_estimators=80, contamination="auto", random_state=seed).fit(X)
    meta_inputs = np.column_stack([b1.predict_proba(X_future)[:, 1], b2.predict_proba(X_future)[:, 1],
                                   -novelty.decision_function(X_future)])
    p = meta.predict_proba(meta_inputs)[:, 1]
    hard = p >= .5
    metrics = {"future_auroc": round(float(roc_auc_score(y_future, p)), 4),
               "future_auprc": round(float(average_precision_score(y_future, p)), 4),
               "future_f1_at_0_5": round(float(f1_score(y_future, hard)), 4),
               "future_samples": len(test_rows), "training_samples": len(train_rows),
               "oof_samples": int(eligible.sum()), "future_cases": len(test_cases),
               "train_cases": len(train_cases)}
    output = Path(output)
    predictions = [{"txid": r["txid"], "score": round(float(s * 100), 4), "split": "future_holdout"}
                   for r, s in zip(test_rows, p, strict=True)]
    _json(output / "predictions.json", {"score_type": "synthetic_future_holdout_ranking_not_real_world_probability",
                                        "predictions": predictions, "features": FEATURE_NAMES})
    report = {"kind": "SYNTHETIC_DEMO_ONLY", "not_real_world_validation": True,
              "label_unit": "transaction, grouped by fictional case", "split": "chronological case grouped 80/20",
              "oof": "4 chronological folds on train cases; first fold excluded from meta training if class deficient",
              "base_models": ["logistic_regression", "random_forest", "isolation_forest_anomaly_score"],
              "meta_model": "logistic_regression_on_oof", "metrics": metrics,
              "leakage_policy": "feature extraction before time split only uses each tx + prevout, never later graph edges"}
    _json(output / "training_report.json", report)
    return report
