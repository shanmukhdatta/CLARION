"""Versioned canonical evidence contracts. All money is integer satoshis.

Only observed wire relations are allowed. No address->host owner relation exists.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha256
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)


def utc(ts: datetime) -> datetime:
    if ts.tzinfo is None or ts.utcoffset() is None:
        raise ValueError("UTC-offset-aware event_time/available_at required")
    return ts.astimezone(timezone.utc)


class EvidenceSource(Strict):
    source_id: str = Field(min_length=1, max_length=128)
    kind: Literal["sih", "bitcoin_core", "elliptic_pp", "bitcoinheist", "synthetic", "canonical"]
    sha256_hex: str = Field(pattern=r"^[0-9a-f]{64}$")
    licence: str = Field(min_length=1)
    origin: str = Field(min_length=1)
    imported_at: datetime

    @field_validator("imported_at")
    @classmethod
    def _time(cls, value: datetime) -> datetime:
        return utc(value)


class Tx(Strict):
    txid: str = Field(pattern=r"^[0-9a-f]{64}$")
    event_time: datetime
    available_at: datetime
    source_id: str
    coinbase: bool = False
    vbytes: int | None = Field(default=None, ge=1)
    fee_sats: int | None = Field(default=None, ge=0)
    block_height: int | None = Field(default=None, ge=0)
    confirmation: Literal["mempool", "confirmed", "orphaned", "unknown"] = "unknown"

    @field_validator("event_time", "available_at")
    @classmethod
    def _time(cls, value: datetime) -> datetime:
        return utc(value)

    @model_validator(mode="after")
    def _availability(self) -> "Tx":
        if self.available_at < self.event_time:
            raise ValueError("available_at cannot precede event_time")
        return self


class Input(Strict):
    txid: str = Field(pattern=r"^[0-9a-f]{64}$")
    vin: int = Field(ge=0)
    prev_txid: str = Field(pattern=r"^[0-9a-f]{64}$")
    prev_vout: int = Field(ge=0)
    source_id: str


class Output(Strict):
    txid: str = Field(pattern=r"^[0-9a-f]{64}$")
    vout: int = Field(ge=0)
    value_sats: int = Field(ge=0, le=21_000_000 * 100_000_000)
    address: str | None = None
    script_type: str | None = None
    source_id: str


class WireObservation(Strict):
    observation_id: str = Field(min_length=1)
    sensor_id: str = Field(min_length=1)
    host: str = Field(min_length=1)
    event_time: datetime
    available_at: datetime
    txid: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    decode_provenance: Literal["observed_inv", "observed_tx", "none"] = "none"
    clock_uncertainty_ms: int = Field(ge=0)
    direction: Literal["in", "out", "unknown"] = "unknown"
    source_id: str
    asn: int | None = Field(default=None, ge=0)
    country: str | None = None

    @field_validator("event_time", "available_at")
    @classmethod
    def _time(cls, value: datetime) -> datetime:
        return utc(value)

    @model_validator(mode="after")
    def _match_provenance(self) -> "WireObservation":
        if self.txid is not None and self.decode_provenance == "none":
            raise ValueError("TXID requires observed decode provenance")
        if self.available_at < self.event_time:
            raise ValueError("wire available_at before event_time")
        return self


class Label(Strict):
    subject_id: str
    subject_type: Literal["transaction", "address", "candidate_entity", "subgraph"]
    value: int = Field(ge=0, le=1)
    available_at: datetime
    source_id: str
    definition: str = Field(min_length=1)

    @field_validator("available_at")
    @classmethod
    def _time(cls, value: datetime) -> datetime:
        return utc(value)


class Edge(Strict):
    edge_id: str
    source: str
    target: str
    relation: Literal[
        "spends_outpoint", "funds_address", "observed_relay",
        "hosted_in", "located_in", "candidate_member", "co_session"
    ]
    event_time: datetime
    available_at: datetime
    source_id: str
    evidence_ref: str
    amount_sats: int | None = Field(default=None, ge=0)
    observed: bool = True

    @field_validator("event_time", "available_at")
    @classmethod
    def _time(cls, value: datetime) -> datetime:
        return utc(value)


class Mode(StrEnum):
    CHAIN_ONLY = "CHAIN_ONLY"
    CROSS_LAYER_ELIGIBLE = "CROSS_LAYER_ELIGIBLE"
    UNSUPERVISED_ONLY = "UNSUPERVISED_ONLY"


class Abstention(Strict):
    status: Literal["ABSTAIN"] = "ABSTAIN"
    reason: str = Field(min_length=1)
    missing: tuple[str, ...] = ()


class Readiness(Strict):
    mode: Mode
    labeled: bool
    wire_join_coverage: float = Field(ge=0, le=1)
    independent_sensors: int = Field(ge=0)
    reasons: tuple[str, ...] = ()


class Snapshot(Strict):
    cutoff: datetime
    transactions: tuple[Tx, ...]
    inputs: tuple[Input, ...]
    outputs: tuple[Output, ...]
    wire: tuple[WireObservation, ...]
    edges: tuple[Edge, ...]
    readiness: Readiness
    source_hashes: dict[str, str]

    @field_validator("cutoff")
    @classmethod
    def _time(cls, value: datetime) -> datetime:
        return utc(value)


def evidence_id(*parts: object) -> str:
    return sha256("|".join(str(p) for p in parts).encode("utf-8")).hexdigest()[:24]
