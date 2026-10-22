"""Safe JSON-serializable chronological logistic baseline, no pickle execution.

Separate experimental supervised modeling from production/unsupervised evidence.
Every inference is score-typed UNCALIBRATED and must be validated externally.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from math import exp, isfinite
from pathlib import Path
from typing import Any

from clarion.v4.ml import FEATURES


def _matrices(rows: list[dict[str, object]], medians: list[float]) -> list[list[float]]:
    result = []
    for row in rows:
        out = []
        for key, median in zip(FEATURES, medians, strict=True):
            raw = row.get(key)
            value = median if raw is None else float(raw)
            if not isfinite(value):
                value = median
            out.append(value)
        result.append(out)
    return result


def fit_json_logistic(
    rows: list[dict[str, object]], labels: dict[str, tuple[int, str]], *,
    source_hashes: dict[str, str], evaluation_time: str, seed: int = 26,
    test_fraction: float = 0.2,
) -> tuple[dict[str, object], dict[str, object]]:
    """Chronological train/future holdout, with historical label availability gate.

    Artifact fits historical training subjects only and excludes holdout labels.
    Labels from a post-training period may score evaluation only, never fit.
    """
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import average_precision_score, roc_auc_score

    if not 0.1 <= test_fraction <= 0.4:
        raise ValueError("invalid holdout share")
    eligible = sorted(
        [r for r in rows if str(r["subject_id"]) in labels and
         str(r["available_at"]) <= evaluation_time and
         labels[str(r["subject_id"])][1] <= evaluation_time],
        key=lambda r: (str(r["available_at"]), str(r["subject_id"])),
    )
    if len(eligible) < 40:
        raise ValueError("at least 40 time-eligible labeled records needed")
    split = int(len(eligible) * (1.0 - test_fraction))
    past, future = eligible[:split], eligible[split:]
    future_start = str(future[0]["available_at"])
    past = [r for r in past if labels[str(r["subject_id"])][1] <= future_start]
    if len(past) < 25 or max(str(r["available_at"]) for r in past) >= future_start:
        raise ValueError("training/future split is overlapping or too small")
    ytrain = np.array([labels[str(r["subject_id"])][0] for r in past], dtype=int)
    ytest = np.array([labels[str(r["subject_id"])][0] for r in future], dtype=int)
    if set(ytrain) != {0, 1} or set(ytest) != {0, 1}:
        raise ValueError("both classes required in train and independently scored holdout")
    rawtrain = np.array([
        [float("nan") if r.get(k) is None else float(r[k]) for k in FEATURES]
        for r in past
    ])
    if any(np.isnan(rawtrain[:,i]).all() for i in range(len(FEATURES))):
        raise ValueError("a training feature is entirely missing")
    median = np.nanmedian(rawtrain, axis=0)
    xtrain = np.asarray(_matrices(past, median.tolist()), dtype=float)
    xfuture = np.asarray(_matrices(future, median.tolist()), dtype=float)
    mean = xtrain.mean(axis=0)
    scale = xtrain.std(axis=0)
    scale[scale < 1e-10] = 1.0
    model = LogisticRegression(max_iter=800, class_weight="balanced", random_state=seed)
    model.fit((xtrain - mean) / scale, ytrain)
    scores = model.predict_proba((xfuture - mean) / scale)[:, 1]
    raw_artifact: dict[str, object] = {
        "format": "CLARION_LOGISTIC_JSON_V1",
        "features": list(FEATURES),
        "median": median.tolist(), "mean": mean.tolist(), "scale": scale.tolist(),
        "coef": model.coef_[0].tolist(), "intercept": float(model.intercept_[0]),
        "training_last_seen": max(str(r["available_at"]) for r in past),
        "train_count": len(past), "heldout_count": len(future),
        "source_hashes": source_hashes,
        "score_type": "SUPERVISED_UNCALIBRATED_NOT_ILLICIT_PROBABILITY",
    }
    encoded = json.dumps(raw_artifact, sort_keys=True, allow_nan=False)
    artifact = {**raw_artifact,
                "payload_sha256": hashlib.sha256(encoded.encode("utf-8")).hexdigest()}
    report = {
        "status": "EXPERIMENTAL_UNCALIBRATED",
        "holdout_auroc": round(float(roc_auc_score(ytest, scores)), 6),
        "holdout_auprc": round(float(average_precision_score(ytest, scores)), 6),
        "evaluated_subject_ids": [str(r["subject_id"]) for r in future],
        "train_count": len(past), "holdout_count": len(future),
        "warning": "Scores are not validated real-world crime probabilities",
    }
    return artifact, report


def predict_json_logistic(
    artifact: dict[str, object], rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    if artifact.get("format") != "CLARION_LOGISTIC_JSON_V1" or artifact.get("features") != list(FEATURES):
        raise ValueError("incompatible model artifact feature contract")
    payload = {k: v for k, v in artifact.items() if k != "payload_sha256"}
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, allow_nan=False).encode()).hexdigest()
    if digest != artifact.get("payload_sha256"):
        raise ValueError("model JSON digest mismatch")
    d = len(FEATURES)
    params = [artifact.get(k) for k in ("median", "mean", "scale", "coef")]
    if any(not isinstance(p, list) or len(p) != d for p in params):
        raise ValueError("model parameter dimension mismatch")
    median, mean, scale, coef = ([float(v) for v in p] for p in params)
    if any(not isfinite(v) for a in (median, mean, scale, coef) for v in a):
        raise ValueError("nonfinite model parameters")
    if any(v <= 0 for v in scale):
        raise ValueError("invalid normalization scale")
    intercept = float(artifact["intercept"])
    if not isfinite(intercept):
        raise ValueError("nonfinite model intercept")
    values = _matrices(rows, median)
    predictions = []
    for row, v in zip(rows, values, strict=True):
        if str(row.get("available_at", "")) < str(artifact["training_last_seen"]):
            raise ValueError("cannot serve newly fitted model retroactively on past subjects")
        score_raw = intercept + sum(
            w * ((x - a) / b)
            for x, a, b, w in zip(v, mean, scale, coef, strict=True)
        )
        score = 1.0 / (1.0 + exp(-max(-700.0, min(700.0, score_raw))))
        predictions.append({
            "subject_id": str(row["subject_id"]),
            "score": round(score, 8),
            "score_type": "SUPERVISED_UNCALIBRATED_NOT_ILLICIT_PROBABILITY",
            "model_sha256": artifact["payload_sha256"],
        })
    return predictions


def save_model_artifact(path: Path, artifact: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True, allow_nan=False) + "\n",
                    encoding="utf-8")


def load_model_artifact(path: Path, *, maximum_bytes: int = 100_000) -> dict[str, object]:
    if not path.is_file() or path.is_symlink() or path.stat().st_size > maximum_bytes:
        raise ValueError("missing, symlink or oversized model JSON")
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("model JSON must be an object")
    # Validate digest, feature schema and numeric parameters before any scoring.
    predict_json_logistic(obj, [])
    return obj
