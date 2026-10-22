"""Offline operational trust boundaries for CLARION source and case files."""
from __future__ import annotations

import ipaddress
from pathlib import Path
from typing import Any


def safe_local_file(path: str | Path, root: str | Path, *, max_bytes: int = 80_000_000) -> Path:
    base=Path(root).resolve(strict=True)
    candidate=Path(path)
    if any(part==".." for part in candidate.parts):
        raise ValueError("path traversal rejected")
    resolved=(base/candidate).resolve(strict=True) if not candidate.is_absolute() else candidate.resolve(strict=True)
    if not resolved.is_relative_to(base) or not resolved.is_file() or resolved.is_symlink():
        raise ValueError("file path outside approved evidence root")
    if resolved.stat().st_size>max_bytes:
        raise ValueError("evidence upload too large")
    return resolved


def local_bind_allowed(host: str) -> bool:
    """API must not accidentally bind to a network-exposed interface."""
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return host=="localhost"


def redact_record(obj: Any, *, include_ip: bool = False) -> Any:
    """Recursively avoid accidental raw IP distribution in public dossier export."""
    if isinstance(obj,list):
        return [redact_record(v,include_ip=include_ip) for v in obj]
    if isinstance(obj,dict):
        answer={}
        for key,val in obj.items():
            if not include_ip and key.lower() in ("ip","host","src_ip","dst_ip","remote_ip"):
                answer[key]="[REDACTED_HOST]"
            else:
                answer[key]=redact_record(val,include_ip=include_ip)
        return answer
    return obj


def reject_csv_formula(value: str) -> str:
    return "'"+value if value.lstrip().startswith(("=","+","-","@")) else value
