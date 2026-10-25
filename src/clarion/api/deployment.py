"""Explicit container-only application entrypoint.

Use in a container whose exposed port is restricted to host loopback.
For direct workstation access, keep `clarion serve` bound to 127.0.0.1.
"""
from __future__ import annotations

import os
from pathlib import Path

from clarion.api.main import create_app

app = create_app(Path(os.environ.get("CLARION_RUN_DIR", "artifacts/submission_demo/investigation")))
