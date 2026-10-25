#!/bin/sh
# Prepare local SYNTHETIC-only example, then serve prebuilt React+FastAPI.
set -eu
cd /workspace
if [ ! -f "${CLARION_RUN_DIR}/run_manifest.json" ]; then
  python scripts/submission_demo.py run --out artifacts/submission_demo --cases 10 --seed 26
fi
python scripts/release/check_submission.py --run "${CLARION_RUN_DIR}"
exec python -m uvicorn clarion.api.deployment:app --host 0.0.0.0 --port 8000 --no-access-log
