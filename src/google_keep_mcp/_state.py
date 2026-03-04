"""Shared mutable state for the Keep client singleton."""
from __future__ import annotations
import gkeepapi

_keep: gkeepapi.Keep | None = None


def get_keep() -> gkeepapi.Keep:
    """Return the authenticated Keep client, raising if not yet initialized."""
    if _keep is None:
        raise RuntimeError("Keep client not initialized. Server may not have started correctly.")
    return _keep
