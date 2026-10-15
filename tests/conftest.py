"""Shared pytest setup for CLARION.

CLARION must run fully offline, so every test runs with network access blocked:
TCP/UDP connections, UDP sends and DNS lookups all raise immediately. Local Unix
sockets (inter-process communication on the same machine) still work.
"""

from __future__ import annotations

import socket
from typing import Any

import pytest

BLOCKED_MESSAGE = "network access blocked during tests"

_real_connect = socket.socket.connect
_real_connect_ex = socket.socket.connect_ex
_real_sendto = socket.socket.sendto


def _is_local_unix(sock: socket.socket) -> bool:
    return sock.family == socket.AF_UNIX


def _guarded_connect(self: socket.socket, address: Any) -> None:
    if _is_local_unix(self):
        return _real_connect(self, address)
    raise RuntimeError(f"{BLOCKED_MESSAGE}: connect to {address!r}")


def _guarded_connect_ex(self: socket.socket, address: Any) -> int:
    if _is_local_unix(self):
        return _real_connect_ex(self, address)
    raise RuntimeError(f"{BLOCKED_MESSAGE}: connect to {address!r}")


def _guarded_sendto(self: socket.socket, *args: Any) -> int:
    if _is_local_unix(self):
        return _real_sendto(self, *args)
    raise RuntimeError(f"{BLOCKED_MESSAGE}: sendto {args[-1]!r}")


def _blocked_lookup(*args: Any, **kwargs: Any) -> Any:
    raise RuntimeError(f"{BLOCKED_MESSAGE}: DNS lookup of {args[0]!r}")


@pytest.fixture(autouse=True)
def _block_network(monkeypatch: pytest.MonkeyPatch) -> None:
    # RuntimeError (not OSError) so retry/except-OSError code cannot swallow the attempt.
    monkeypatch.setattr(socket.socket, "connect", _guarded_connect)
    monkeypatch.setattr(socket.socket, "connect_ex", _guarded_connect_ex)
    monkeypatch.setattr(socket.socket, "sendto", _guarded_sendto)
    monkeypatch.setattr(socket, "getaddrinfo", _blocked_lookup)
    monkeypatch.setattr(socket, "gethostbyname", _blocked_lookup)
