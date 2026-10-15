"""Typed errors raised by CLARION. Each message says what failed and where."""


class ClarionError(Exception):
    """Base class for every error CLARION raises on purpose."""


class ConfigError(ClarionError):
    """A run profile is missing, malformed, unsafe or breaks a CLARION rule."""
