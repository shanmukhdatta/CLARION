"""Bounded canonical CSV/JSON/XML adapters and deterministic quarantine.

Unrecognized provider columns are rejected: published datasets have different units
and label semantics. Explicit mappings and source manifests are mandatory.
"""
from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable, TypeVar
from xml.etree import ElementTree

from pydantic import ValidationError

from clarion.v4.contracts import (
    EvidenceSource, Input, Label, Output, Tx, WireObservation,
)

MAX_FILE_BYTES = 80_000_000
MAX_ROWS = 250_000
MAX_XML_BYTES = 2_000_000
T = TypeVar("T")


def btc_to_sats(value: str) -> int:
    try:
        d = Decimal(value)
        sats = d * 100_000_000
        if not d.is_finite() or d < 0 or sats != sats.to_integral_value():
            raise ValueError("BTC value is negative, non-finite, or sub-satoshi")
        return int(sats)
    except (InvalidOperation, TypeError) as exc:
        raise ValueError(f"invalid BTC decimal: {value!r}") from exc


def load_rows(path: Path, maximum: int = MAX_ROWS) -> list[dict[str, Any]]:
    if not path.is_file() or path.is_symlink():
        raise ValueError("source must be a regular file and not a symlink")
    if path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError(f"oversize source: {path.name}")
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as fp:
            reader = csv.DictReader(fp)
            if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
                raise ValueError("missing or duplicated CSV header")
            rows = []
            for i, row in enumerate(reader):
                if i >= maximum:
                    raise ValueError("too many source rows")
                if None in row:
                    raise ValueError("CSV row has extra columns")
                rows.append(dict(row))
            return rows
    if path.suffix.lower() == ".json":
        obj = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(obj, dict):
            obj = obj.get("records")
        if not isinstance(obj, list) or len(obj) > maximum or not all(isinstance(x, dict) for x in obj):
            raise ValueError("JSON must be an array of bounded record objects")
        return obj
    if path.suffix.lower() == ".xml":
        if path.stat().st_size > MAX_XML_BYTES:
            raise ValueError("XML file exceeds restrictive import limit")
        data = path.read_bytes()
        if b"<!DOCTYPE" in data.upper() or b"<!ENTITY" in data.upper():
            raise ValueError("external entities/DTDs prohibited")
        try:
            from defusedxml import ElementTree as SafeET
        except ImportError as exc:
            raise RuntimeError("XML import requires defusedxml") from exc
        root = SafeET.fromstring(data)
        elements = list(root)
        if len(elements) > maximum:
            raise ValueError("too many XML records")
        return [{child.tag: child.text for child in row} for row in elements]
    raise ValueError("supported input formats: CSV, JSON, restricted XML")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fp:
        for block in iter(lambda: fp.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


@dataclass(frozen=True)
class ImportResult:
    transactions: list[Tx]
    inputs: list[Input]
    outputs: list[Output]
    wire: list[WireObservation]
    labels: list[Label]
    quarantine: list[dict[str, Any]]
    hashes: dict[str, str]


def _parse_time(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str):
        raise ValueError("ISO8601 offset-aware timestamp required")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timezone offset required")
    return parsed.astimezone(timezone.utc)


def _int(value: Any) -> int:
    if isinstance(value, bool) or not str(value).isdigit():
        raise ValueError(f"integer required, got {value!r}")
    return int(value)


def _normalize(table: str, row: dict[str, Any], source_id: str) -> dict[str, Any]:
    # Synthetic demo aliases are the only built-in legacy adapter.
    r = dict(row)
    if table == "transactions":
        r["event_time"] = _parse_time(r.pop("time", r.get("event_time")))
        r["available_at"] = _parse_time(r.get("available_at", r["event_time"]))
        r["coinbase"] = str(r.get("coinbase", "0")).lower() in ("true", "1")
        for key in ("vbytes", "fee_sats", "block_height"):
            if key in r and r[key] not in (None, ""):
                r[key] = _int(r[key])
        r.pop("case_id", None)
    elif table == "inputs":
        for key in ("vin", "prev_vout"):
            r[key] = _int(r[key])
    elif table == "outputs":
        r["vout"] = _int(r["vout"])
        r["value_sats"] = _int(r["value_sats"])
    elif table == "observations":
        r["event_time"] = _parse_time(r.pop("time", r.get("event_time")))
        r["available_at"] = _parse_time(r.get("available_at", r["event_time"]))
        r["host"] = r.pop("host", r.pop("src_ip", None))
        r["observation_id"] = r.get("observation_id") or f"{source_id}:{hashlib.sha256(json.dumps(row, sort_keys=True).encode()).hexdigest()[:20]}"
        r["txid"] = r.get("txid") or None
        r["decode_provenance"] = r.get("decode_provenance", "observed_inv" if r["txid"] else "none")
        r["clock_uncertainty_ms"] = _int(r.get("clock_uncertainty_ms", "1000"))
        r.pop("event", None)
    elif table == "labels":
        r["available_at"] = _parse_time(r["available_at"])
        r["value"] = _int(r["value"])
    r["source_id"] = source_id
    return r


def import_canonical(
    root: str | Path, *, licence: str, origin: str, kind: str = "canonical",
    include_labels: bool = False, max_rejected: int = 1000,
) -> ImportResult:
    """Import files named transactions/inputs/outputs/observations/labels.

    For production, identify each provider schema and transform to this contract.
    No labels are loaded into evidence during inference without explicit request.
    """
    directory = Path(root)
    if not licence.strip() or not origin.strip():
        raise ValueError("licence and origin are required")
    model_map: dict[str, Any] = {
        "transactions": Tx, "inputs": Input, "outputs": Output,
        "observations": WireObservation, "labels": Label,
    }
    required = {"transactions", "inputs", "outputs"}
    paths: dict[str, Path] = {}
    for key in model_map:
        if key == "labels" and not include_labels:
            continue
        for extension in (".csv", ".json", ".xml"):
            path = directory / (key + extension)
            if path.exists():
                paths[key] = path
                break
        if key in required and key not in paths:
            raise FileNotFoundError(f"missing canonical {key} table")
    values: dict[str, list[Any]] = {key: [] for key in model_map}
    quarantine: list[dict[str, Any]] = []
    hashes: dict[str, str] = {}
    for key, path in paths.items():
        hashes[key] = digest(path)
        for index, row in enumerate(load_rows(path), start=2):
            try:
                normalized = _normalize(key, row, key + ":" + hashes[key][:12])
                values[key].append(model_map[key].model_validate(normalized))
            except (ValueError, ValidationError, TypeError, KeyError) as exc:
                quarantine.append({"table": key, "row": index, "error": str(exc)[:250]})
                if len(quarantine) > max_rejected:
                    raise ValueError("quarantine exceeds configured limit") from exc
    return ImportResult(
        transactions=values["transactions"], inputs=values["inputs"],
        outputs=values["outputs"], wire=values["observations"],
        labels=values["labels"], quarantine=quarantine, hashes=hashes,
    )


def import_bitcoin_core_tx(tx: dict[str, Any], *, source_id: str, available_at: datetime) -> tuple[Tx, list[Input], list[Output]]:
    """Adapter for Bitcoin Core getrawtransaction verbosity=2 with prevout support.

    Bitcoin Core prevout is not assured; unresolved value and fee stay null.
    """
    when = _parse_time(tx.get("blocktime", tx.get("time"))) if "blocktime" in tx or "time" in tx else available_at
    inputs = []
    coinbase = any("coinbase" in v for v in tx.get("vin", []))
    for vin_no, v in enumerate(tx.get("vin", [])):
        if "coinbase" not in v:
            inputs.append(Input(txid=tx["txid"], vin=vin_no, prev_txid=v["txid"], prev_vout=_int(v["vout"]), source_id=source_id))
    outputs = []
    for v in tx.get("vout", []):
        script = v.get("scriptPubKey", {})
        address = script.get("address")
        if address is None and len(script.get("addresses", [])) == 1:
            address = script["addresses"][0]
        outputs.append(Output(txid=tx["txid"], vout=_int(v["n"]), value_sats=btc_to_sats(str(v["value"])), address=address, script_type=script.get("type"), source_id=source_id))
    fee_sats = btc_to_sats(str(tx["fee"])) if "fee" in tx and Decimal(str(tx["fee"])) >= 0 else None
    return Tx(txid=tx["txid"], event_time=when, available_at=available_at, source_id=source_id,
              coinbase=coinbase, vbytes=tx.get("vsize"), fee_sats=fee_sats,
              confirmation="confirmed" if tx.get("confirmations", 0) > 0 else "unknown"), inputs, outputs


def declared_mapping_adapter(
    rows: Iterable[dict[str, Any]], mapping: dict[str, str], *,
    required: set[str], source_kind: str,
) -> list[dict[str, Any]]:
    """Explicit import mapping for SIH/Elliptic++/BitcoinHeist (never guessed).

    Tabular feature-only datasets cannot invent UTXO outpoints, IPs, or owners.
    """
    if source_kind not in ("sih", "elliptic_pp", "bitcoinheist"):
        raise ValueError("unknown provider type")
    if not required.issubset(mapping):
        raise ValueError(f"missing required canonical columns: {sorted(required - set(mapping))}")
    result = []
    for row in rows:
        if any(src not in row for src in mapping.values()):
            raise ValueError("mapping refers to missing provider columns")
        result.append({dst: row[src] for dst, src in mapping.items()})
    return result
