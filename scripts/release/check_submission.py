"""Read-only gate: refuse misleading model/data claims before an offline showcase."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from clarion.v4.submission import inspect_run


def main() -> int:
    p = argparse.ArgumentParser(description="CLARION synthetic demonstration release check")
    p.add_argument("--run", required=True)
    p.add_argument("--model")
    args = p.parse_args()
    report = inspect_run(Path(args.run), args.model)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
