"""Observed P2P relay sessionization and contextual feature extraction.

A TXID seen from a host is an observation, never evidence of its origin,
the controller's geography, or a Bitcoin wallet's owner.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from math import log2

from clarion.v4.contracts import WireObservation, utc


@dataclass(frozen=True)
class RelaySession:
    session_id: str
    sensor_id: str
    host: str
    first_seen: str
    last_seen: str
    observation_ids: tuple[str, ...]
    observed_txids: tuple[str, ...]
    source_ids: tuple[str, ...]
    event_count: int
    port_entropy: float | None

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def _entropy(values: list[int]) -> float | None:
    if not values:
        return None
    counts: dict[int, int] = defaultdict(int)
    for value in values:
        counts[value] += 1
    return round(-sum((n / len(values)) * log2(n / len(values))
                      for n in counts.values()), 6)


def build_sessions(
    observations: tuple[WireObservation, ...] | list[WireObservation], *,
    gap_seconds: int = 300,
    cutoff: datetime,
) -> list[RelaySession]:
    """Session keys are sensor+observed host; timestamps are source-provenance only.

    Repeated sensor/host/txid/time facts are deduplicated. Sensor independence
    must be validated separately; multiple sensors do not prove initiation.
    """
    if not 1 <= gap_seconds <= 86400:
        raise ValueError("gap_seconds must be between 1 and 86400")
    effective = utc(cutoff)
    streams: dict[tuple[str, str], list[WireObservation]] = defaultdict(list)
    seen: set[tuple[str, str, str | None, datetime]] = set()
    for obs in observations:
        if obs.available_at > effective or obs.event_time > effective:
            continue
        key = (obs.sensor_id, obs.host, obs.txid, obs.event_time)
        if key not in seen:
            streams[(obs.sensor_id, obs.host)].append(obs)
            seen.add(key)
    sessions: list[RelaySession] = []
    for (sensor, host), records in sorted(streams.items()):
        ordered = sorted(records, key=lambda o: (o.event_time, o.observation_id))
        groups: list[list[WireObservation]] = []
        for event in ordered:
            if not groups or event.event_time - groups[-1][-1].event_time > timedelta(seconds=gap_seconds):
                groups.append([event])
            else:
                groups[-1].append(event)
        for index, group in enumerate(groups):
            import hashlib

            uid = hashlib.sha256(
                f"{sensor}|{host}|{index}|{group[0].event_time.isoformat()}".encode()
            ).hexdigest()[:20]
            ports = [port for obs in group for port in
                     (obs.source_port, obs.destination_port) if port is not None]
            sessions.append(RelaySession(
                session_id="session:" + uid,
                sensor_id=sensor, host=host,
                first_seen=group[0].event_time.isoformat(),
                last_seen=group[-1].event_time.isoformat(),
                observation_ids=tuple(o.observation_id for o in group),
                observed_txids=tuple(sorted({o.txid for o in group if o.txid is not None})),
                source_ids=tuple(sorted({o.source_id for o in group})),
                event_count=len(group), port_entropy=_entropy(ports),
            ))
    return sessions


def wire_feature_rows(
    observations: tuple[WireObservation, ...] | list[WireObservation], *,
    cutoff: datetime,
) -> list[dict[str, object]]:
    """Per-observed-TXID descriptive features; no ownership inference or risk scoring."""
    stamp = utc(cutoff)
    groups: dict[str, list[WireObservation]] = defaultdict(list)
    for obs in observations:
        if obs.txid is not None and obs.decode_provenance != "none" and (
            obs.event_time <= stamp and obs.available_at <= stamp
        ):
            groups[obs.txid].append(obs)
    rows = []
    for txid, events in sorted(groups.items()):
        timestamps = [o.event_time for o in events]
        rows.append({
            "txid": txid,
            "unique_observing_hosts": len({o.host for o in events}),
            "unique_sensors": len({o.sensor_id for o in events}),
            "observations": len(events),
            "first_seen": min(timestamps).isoformat(),
            "last_seen": max(timestamps).isoformat(),
            "time_span_seconds": (max(timestamps) - min(timestamps)).total_seconds(),
            "max_clock_uncertainty_ms": max(o.clock_uncertainty_ms for o in events),
            "source_ids": sorted({o.source_id for o in events}),
            "claim": "OBSERVED_RELAY_ONLY_NOT_ORIGIN_OR_WALLET",
        })
    return rows
