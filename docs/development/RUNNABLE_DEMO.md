# CLARION v4 — runnable offline synthetic demonstration

A **working research prototype**, NOT a verified production risk detector. Implements
synthetic generation, exact Bitcoin-style UTXO accounting, permitted relay observations,
readiness routing, as-of features, witness-based peel-like motifs, time-grouped OOF
logistic/forest/novelty stacking, a bounded two-pass risk ranking, explainable
JSON/CSV run artifacts, and a localhost-only read-only dashboard.

The demo deliberately **abstains** on Δ (independent chain/wire dependence not
verified) and Π (economic goal unavailable). Host relay observations never imply
wallet ownership, and synthetic scores never imply actual criminal behavior.

## Requirements

Python **3.11 or 3.12**. Install on Linux/Windows/macOS (internet required to install
packages initially, no internet required to run):

```bash
python -m venv .venv
source .venv/bin/activate      # on Windows: .venv\\Scripts\\activate
python -m pip install -r requirements-demo.txt -e .
python -m pip install pytest httpx
```

## Run all stages

```bash
clarion generate-demo --out data/generated/demo --cases 90 --seed 26
clarion validate --data data/generated/demo
clarion train-demo --data data/generated/demo --out artifacts/demo_training
clarion investigate --data data/generated/demo --out artifacts/demo_run --predictions artifacts/demo_training/predictions.json
clarion serve --run artifacts/demo_run --port 8000
```

Open `http://127.0.0.1:8000` on the **same machine**. To run regression tests:

```bash
PYTHONPATH=src python -m pytest -q  # Windows PowerShell: $env:PYTHONPATH='src'; python -m pytest -q
```

The executable is also available as `PYTHONPATH=src python -m clarion.cli.main`.
`bash scripts/demo.sh` runs all non-server stages on Linux. A starter synthetic
36-case fixture is available in `data/samples/small` in the full deliverable.

## Inputs and outputs

`transactions.csv`, `inputs.csv`, `outputs.csv`, and `observations.csv` are the
synthetic **evidence** inputs. `truth_SYNTHETIC_ONLY.csv` is an independent label
sidecar used **only by train-demo**. `source_manifest.json` carries the source
provenance warning. Training writes `training_report.json` plus future holdout
`predictions.json`. Investigation writes `leads.json`, `leads.csv`, `graph.json`,
`motifs.json`, `propagation.json`, `entities.json`, and `run_manifest.json`.

Rows contain exact integer satoshis, UTC timestamps, `txid:vout` references,
source/case IDs. Case/group chronological splitting prevents split-through labels
across the same synthetic spending episode. The training output is an **investigative
ranking demonstration**, not calibrated illicit-activity probabilities.

## What is not implemented or validated

Full chain+wire **Δ** hypothesis and chain/wire dependence significance testing;
objective-based **Π** counterfactual expenditure; trained GraphSAGE/GAT;
MCER confidence optimizer and lineage; IP/ASN enrichment; service hard-barrier
validation; production-grade authentication and offline installers; real chain
adapters and independently labeled data. The complete repository v4 roadmap
remains the design authority for these follow-on research components. Unmet
evidence prerequisites are intentionally not faked by the demo.

The test suite verifies deterministic generation, UTXO conservation, duplicate
spend detection, UTC enforcement, future-time exclusion, graph witness paths,
host isolation, propagation bounds, abstention, temporal training, and read-only
API surface. The result is a reproducible small-data demonstration, not a SIH
benchmark claim.
