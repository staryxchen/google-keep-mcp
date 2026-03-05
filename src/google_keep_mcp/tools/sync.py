from __future__ import annotations
from mcp.server.fastmcp import FastMCP

from ..models import ToolResult
from .._state import get_keep


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def sync() -> ToolResult:
        """Sync with Google Keep servers to fetch the latest changes.

        Call this before reading notes if changes may have been made from
        another client (mobile app, web, etc.) since the server started.
        """
        keep = get_keep()
        keep.sync()
        return ToolResult(success=True, message="Synced with Google Keep")
