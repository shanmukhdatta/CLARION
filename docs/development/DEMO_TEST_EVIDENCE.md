# Local execution evidence — October 22, 2026

- Python 3.11+, numpy 2.3.5, scikit-learn 1.8, FastAPI 0.128.
- `PYTHONPATH=src pytest -q`: **13 tests passed** (includes UTXO exactness,
  double-spend/UTC invalid inputs, safe abstention, chronology, and API tests).
- `bash scripts/demo.sh`: generated **360** fictional transactions (90 cases),
  checked **270** prevout edges, matched **362** synthetic relay observations
  without assuming wallet ownership, produced **270** ranked lead dossiers and
  **33** peel-like motifs.
- Synthetic-only chronological future holdout: 72 train cases, 18 holdout cases;
  168 meta-model OOF predictions; holdout metrics **AUROC 1.0**, **AUPRC 1.0**,
  **F1 1.0**. This reflects an artificially simple generator and **must not**
  be cited as actual detection quality or evidence of real-world generalization.
- CI, GPU acceleration, independent SIH datasets, real wire captures and remote
  deployment **not validated**.
