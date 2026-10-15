"""Entry point for the `clarion` shell command.

Subcommands (doctor, ingest, ...) are added by the phase that implements them.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from clarion import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="clarion",
        description="Offline, explainable Bitcoin transaction and network-traffic intelligence.",
    )
    parser.add_argument("--version", action="version", version=f"clarion {__version__}")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Parse arguments and return a process exit code (0 = success)."""
    parser = build_parser()
    parser.parse_args(argv)
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
