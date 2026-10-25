# CLARION local setup, testing, and synthetic research

Use a Python 3.11–3.12 virtual environment on Linux or WSL. The review UI is a local single-user experiment. This project does **not** contain genuine P2P capture or permissioned labeled investigation data.

## Get code and install\n\nFor the October 25 submission path and explicit research limitations, see [submission integration](submission-architecture.md).

```bash
git clone https://github.com/shanmukhdatta/CLARION.git
cd CLARION
git switch main  # the completed implementation PR is already merged
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e . -r requirements-v4.txt -r requirements-demo.txt pytest ruff
cd frontend
npm install --no-audit --no-fund
npm run typecheck
npm run build
cd ..
```

## Generate canonical fictional inputs, run and inspect

```bash
python -m clarion.cli.main generate-demo --out data/generated/quickstart --cases 36 --seed 26
python scripts/v4_pipeline.py analyze \
  --data data/generated/quickstart \
  --out artifacts/v4_run \
  --licence SYNTHETIC_LOCAL \
  --origin CLARION_GENERATOR
python -m pytest -q
python -m ruff check src/clarion/v4 tests/v4 scripts/v4_pipeline.py
```

Inspect `artifacts/v4_run/run_manifest.json`, `graph.json`, `mcer_evidence.json`, `mcer_partition.json`, `wire_sessions.json`, `wire_features.json`, `propagation.json`, `monitoring.json`, and `quarantine.json`. The score type is **unsupervised novelty / review priority**, not crime probability.

## Local investigation and persistent review

Copy `.env.example` to an ignored local file, replace the placeholder with a locally generated random token, and export it into your shell (do not commit credentials). For example:

```bash
export CLARION_REVIEW_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
export CLARION_REVIEWER_ID=local_operator
clarion serve --run artifacts/v4_run --port 8000
```

Open `http://127.0.0.1:8000`; the built React UI is served if `frontend/dist` exists. The Cases page accepts the token **per deliberate write** and clears it afterward. The API refuses writes without a configured token. Case state is saved separately as `artifacts/v4_run/.clarion_reviews.sqlite3`. Stop writes, back up run hashes and SQLite together.

For live frontend development, launch `cd frontend && npm run dev` while FastAPI runs on port 8000; Vite proxies same-origin `/api`.

## Separate experimental model training

A genuine canonical `labels.csv` must supply `subject_id,subject_type,value,available_at,definition`. Do not use the demo truth file for real-world conclusions.

```bash
python scripts/train/train_json_baseline.py --data YOUR_CANONICAL_DIR --licence YOUR_RIGHTS --origin YOUR_SOURCE --out artifacts/json_model
python scripts/train/predict_json_baseline.py --model artifacts/json_model/logistic_model.json --features artifacts/v4_run/features.json --out artifacts/predictions.json
```

The model refuses future/time-ineligible training cohorts, incompatible feature signatures, tampered JSON artifacts or retroactive inference before training cutoff. Model scores are uncalibrated. Inference requires features available at/after the saved cutoff. Do not use synthetic evaluation results to claim real-world detection accuracy.

## CI and limitations

Check the exact PR SHA's GitHub Actions jobs: Python tests, v4 contracts/Ruff, canonical sample, React typecheck/build, security and doc integrity. The full remaining research gaps and per-requirement outcomes are in [FINAL_FEATURE_AUDIT.md](FINAL_FEATURE_AUDIT.md).
