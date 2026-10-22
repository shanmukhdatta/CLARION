# CLARION v4: from scratch to research validation (no invented results)

> No tests, training or UI build were executed in the static coding pass.
> This page lists **commands for your later testing**.

## A. First prepare dependencies

Python 3.11 or 3.12:

```bash
git clone https://github.com/shanmukhdatta/CLARION.git
cd CLARION
git switch implementation/v4-static-code-orange-ui-20261022
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e . -r requirements-v4.txt pytest
```

For **optional** graph research, install a compatible torch/torch-geometric
CPU/CUDA pair from their upstream compatibility matrix. Never run a large
heterogeneous graph on an unbounded source file.

## B. Inspect sample data (no real data needed)

```bash
python scripts/data/generate_fixtures.py --out data/generated/quickstart --cases 32 --seed 26
```

This creates fictional transactions, exact previous outputs and separate
`truth_SYNTHETIC_ONLY.csv`. Labels are not read for inference.

## C. Run new v4 pipeline

```bash
python scripts/v4_pipeline.py analyze \
  --data data/generated/quickstart \
  --out artifacts/v4_quickstart \
  --licence SYNTHETIC_LOCAL \
  --origin CLARION_fixture_generator
```

The source should produce a bounded, abstaining chain-only report. Check
`run_manifest.json`, `quarantine.json`, `graph.json`, `leads.json`,
and every edge's input outpoint before believing anything.

## D. Start the local frontend

```bash
clarion serve --run artifacts/v4_quickstart --port 8000
# second terminal
cd frontend
npm install
npm run typecheck
npm run dev
```

Open `http://127.0.0.1:5173` for Vite dev mode. For static distribution:
`npm run build` then `clarion serve` serves the built page at
`http://127.0.0.1:8000`. No external telemetry.

## E. Prepare real Bitcoin Core JSON offline

```bash
python scripts/data/prepare_bitcoin_core.py \
  --source data/external/approved_verbose2.json \
  --out data/processed/core_import \
  --licence YOUR_DOCUMENTED_PERMISSION \
  --origin YOUR_BITCOIN_CORE_EXPORT
```

This adapter does **not** invent missing parent outputs or IP sources. Graph
mode remains chain-only absent validated sensor pairing.

## F. Train only after supplying real labels with availability timestamps

The canonical `labels.csv` must contain
`subject_id,subject_type,value,available_at,definition`.
When labels or independent groups cannot support strict future holdout, training
raises an error instead of fabricating a score.

```bash
python scripts/train/run_baselines.py \
  --data data/processed/approved_labeled_canonical \
  --out artifacts/v4_training \
  --licence YOUR_LICENSE \
  --origin YOUR_DATA_PROVIDER
```

Model zoo: logistical/RF supervised, IsolationForest novelty,
TimeSeriesSplit OOF stacked logistic meta-learner; optional PyG GraphSAGE
or GAT embedding challenger. Real labels must come from a vetted public or
authorized source with explicit labeling definition, NOT network relays.

## G. Tests, security, audits and research conclusions

```bash
python -m pytest -q tests/v4
python -m ruff check src/clarion/v4 tests/v4
cd frontend && npm run typecheck && npm run build
```

Or use the **manual dispatch workflow** in GitHub Actions. Conduct negative
controls on missing prevouts, CoinJoin-like, service batching, duplicate relays,
unknown Pi, unverified Delta, and future data, *plus* independent real-data
evaluation before any accuracy claim. Synthetic AUROC is not real AML AUROC.

Full interfaces: [schemas](V4_PIPELINES_AND_SCHEMAS.md).
Honest status: [implementation audit](V4_STATIC_IMPLEMENTATION_STATUS.md).
