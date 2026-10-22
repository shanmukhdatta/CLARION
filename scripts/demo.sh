#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}src"
python -m clarion.cli.main generate-demo --cases 90 --seed 26
python -m clarion.cli.main validate
python -m clarion.cli.main train-demo
python -m clarion.cli.main investigate --predictions artifacts/demo_training/predictions.json
printf 'To launch dashboard: PYTHONPATH=src python -m clarion.cli.main serve\n'
