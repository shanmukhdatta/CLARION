# CLARION submission integration: architecture, phase execution and honest status

> **Status:** additional runnable synthetic acceptance and static showcase code, **not** proof of full v4 research implementation. Revision 2026-10-25. The existing [172-requirement ledger](IMPLEMENTATION_CHECKLIST.md) remains authoritative for unresolved scientific work. No real provenance, sensor capture or labels were invented.

## Purpose and artifacts

The canonical vertical slice is already implemented in `src/clarion/v4/`: bounded ingest → ledger graph → tentative MCER/motifs → unsupervised rank → frozen pass-1 → up-to-six-hop value propagation with ≤25 points added → evidence dossier. This submission layer adds an acceptance inspector, local experiment metadata, optional GraphSAGE research proxy, Github Pages static explanation, and blue/white local visual theme.

| Stage | Executable owner | Input → Output | Readiness and qualification |
|---|---|---|---|
| 01. Rights & input | `v4/ingest.py` | permissioned CSV/JSON/XML → bounded canonical rows | verified fictional sample; real rights need audit |
| 02. Source hashing | `v4/ingest.py` | input bytes → source hashes and quarantine | narrow demo checked |
| 03. Bitcoin UTXO | `v4/graph.py` | inputs/outpoints → value edges | working on fictional inputs; real script/reorg gaps |
| 04. Network observations | `v4/wire_sessions.py` | decoded TXID/sensor → relay facts | fictional sensors only; no wallet ownership |
| 05. Cross-layer join | `v4/graph.py` | exact TXID → observed-relay context | meaningful independent P2P validation blocked |
| 06. Temporal snapshots | `v4/graph.py` | as-of cutoff → typed graph | limited fixtures tested |
| 07. Feature engineering | `v4/graph.py` | source facts → feature rows | source-/time-aware in demo |
| 08. MCER | `v4/mcer.py` | H1/H2 evidence → tentative entity groups | H3–H5 need calibration, false-merge tests |
| 09. Motifs | `v4/analysis.py`, `motifs_extended.py` | witness paths → candidate patterns | incomplete full motif zoo |
| 10. Supervised baselines | `v4/ml.py`, `model_artifact.py` | time-eligible labels → OOF/json artifact | research code; real labels needed |
| 11. Novelty | `v4/ml.py` | features → unsupervised rank | demo can run without credible labels |
| 12. GraphSAGE/GAT | `v4/gnn_training.py`, `representation.py` | graph.json → optional edge proxy model | CPU PyG dependency; *not* crime classifier |
| 13. Δ divergence | `v4/signals.py` | independently paired evidence → research signal | **ABSTAIN** on demo (correct) |
| 14. Π expenditure | `v4/signals.py` | verified economic objective → cost ratios | **ABSTAIN** on demo (correct) |
| 15. First-pass fusion | `v4/analysis.py` | eligible components → frozen ≤75 seed | demonstrative priorities, not calibrated odds |
| 16. MLRP | `v4/analysis.py` | directed UTXO paths → ≤6 hops, ≤25 points | real service boundaries unvalidated |
| 17. Review console | `api/main.py`, `frontend/src/app/App.tsx` | run artifacts → local blue/white UI | React Vite build/CI; case SQLite local |
| 18. API/security | `api/reviews.py`, `v4/security.py` | local authorization → bounded review | no multi-user internet service claims |
| 19. MLOps | `v4/mlops_adapter.py` | synthetic run summary → local JSON/optional MLflow | MLflow optional; no remote tracking |
| 20. Release/showcase | `v4/submission.py`, `docs/index.html` | verified synthetic run → status + public static explanation | Pages static; actual inference stays local |

## Commands (from repository root)

Install the tested baseline dependencies:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e . -r requirements-v4.txt -r requirements-demo.txt pytest ruff
python scripts/submission_demo.py run --out artifacts/submission_demo --cases 10 --seed 26
python scripts/release/check_submission.py --run artifacts/submission_demo/investigation
python scripts/train/record_mlflow.py --run artifacts/submission_demo/investigation --out artifacts/mlops
python -m pytest -q tests/v4
```

The MLflow command works without MLflow installed by recording only `experiment.json`; to enable offline UI tracking, install `requirements-mlops.txt` in an isolated **development environment**. No mandatory network endpoint or API key is required for a local CLARION demo.

Optional GraphSAGE, **only** after manually installing compatible PyTorch and PyTorch Geometric as documented by the official project:

```bash
python scripts/train/run_submission_gnn.py train --graph artifacts/submission_demo/investigation/graph.json --model artifacts/models/graphsage_proxy.json --epochs 12
python scripts/train/run_submission_gnn.py infer --graph artifacts/submission_demo/investigation/graph.json --model artifacts/models/graphsage_proxy.json --source 'tx:...' --target 'tx:...'
```

Choose actual node IDs from `graph.json`. This is an unsupervised edge-reconstruction research proxy: no verified negative labels, no criminality classification, no pretrained real-world model. It uses safe bounded JSON tensors, not untrusted pickle/H5. Static-site preview: `docs/index.html`; configure GitHub Pages with **GitHub Actions** publication; no secrets needed.

## Test scope and open acceptance

CI should pass Python tests, Ruff in the affected v4 directory, canonical 36-case smoke, React typecheck/build and local socket security. Additional tests validate schema/lead score caps, model-not-configured displays and false-owner-link rejection. Real trained/independently validated hetero GNN, authentic TXID wire captures, scientific Δ1–Δ5/Π controlled goals, model calibration, comprehensive privacy hard negatives and complete air-gapped installer are **not** represented as achieved.

**Submission rule:** synthetic data is explicitly labelled and kept out of training-time inference truth channels. An unconfigured model button must display MODEL_NOT_CONNECTED. Never report synthetic AUPRC as real illicit detection efficacy.

## Reviewer checkpoints

- Compare `SUBMISSION_STATUS.json` source hashes and audit result to generated `run_manifest.json` and `leads.json`.
- Assert every lead has local ≤75, propagation ≤25, final ≤100 and explicit score type.
- Verify no IP-to-wallet ownership edges and honest Δ/Π abstention.
- Run local FastAPI/React for genuine interactions; GitHub Pages only showcases architecture.
- For unresolved features, use the [requirements audit](IMPLEMENTATION_CHECKLIST.md) rather than claiming that placeholder modules are complete.

## Single-command synthetic ML + evidence integration (submission-stage extension)

```bash
python scripts/full_demo_pipeline.py --out artifacts/full_demo --cases 36 --seed 26
clarion serve --run artifacts/full_demo/investigation --port 8000
```

This actually runs a **fictional** chronology/grouped out-of-fold Logistic Regression / Random Forest / Isolation Forest stack; saves the measured `training/training_report.json` and future-only `predictions.json`; runs the separate historical synthetic inference example; then builds and audits the primary v4 **unsupervised** evidence investigation. It writes a real `investigation/training_experiment.json` consumed by `GET /api/experiments/demo`, which is surfaced on the dashboard's Models page. No trained checkpoint is falsely declared ready. Optional MLflow writes local aggregate metrics; if MLflow is absent the JSON tracker still records them. Synthetic perfect results can arise from generator simplicity and cannot establish real-world generalization.
