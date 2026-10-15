"""Prove the offline guard in tests/conftest.py really blocks network access.

If these tests fail, every other test's "works offline" result is meaningless.
Later phases add checks that ingestion, inference and the local UI run with it on.
"""

from __future__ import annotations

import socket

import pytest

# Must match BLOCKED_MESSAGE in tests/conftest.py (conftest files are not importable modules).
BLOCKED_MESSAGE = "network access blocked during tests"

# 192.0.2.0/24 is reserved for documentation (RFC 5737) and never routed on the Internet.
UNROUTABLE_IP = "192.0.2.1"


def test_tcp_connection_is_blocked() -> None:
    with pytest.raises(RuntimeError, match=BLOCKED_MESSAGE):
        socket.create_connection((UNROUTABLE_IP, 80), timeout=1)


def test_tcp_connect_ex_is_blocked() -> None:
    with (
        socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock,
        pytest.raises(RuntimeError, match=BLOCKED_MESSAGE),
    ):
        sock.connect_ex((UNROUTABLE_IP, 80))


def test_udp_send_is_blocked() -> None:
    with (
        socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock,
        pytest.raises(RuntimeError, match=BLOCKED_MESSAGE),
    ):
        sock.sendto(b"probe", (UNROUTABLE_IP, 53))


def test_dns_lookup_is_blocked() -> None:
    with pytest.raises(RuntimeError, match=BLOCKED_MESSAGE):
        socket.getaddrinfo("example.com", 443)
    with pytest.raises(RuntimeError, match=BLOCKED_MESSAGE):
        socket.gethostbyname("example.com")


def test_local_unix_socket_pair_still_works() -> None:
    left, right = socket.socketpair()
    with left, right:
        left.sendall(b"ping")
        assert right.recv(4) == b"ping"
