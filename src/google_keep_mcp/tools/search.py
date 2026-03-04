from __future__ import annotations
from mcp.server.fastmcp import FastMCP

from ..models import ListNotesResult
from ..server import get_keep
from ._helpers import note_to_model


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def search_notes(
        query: str,
        include_archived: bool = False,
        include_trashed: bool = False,
    ) -> ListNotesResult:
        """Search notes by text query (matches title and body).

        Args:
            query: Search string to match against note title and text.
            include_archived: Whether to include archived notes in results.
            include_trashed: Whether to include trashed notes in results.
        """
        keep = get_keep()
        results = list(keep.find(
            query=query,
            archived=True if include_archived else False,
            trashed=include_trashed,
        ))
        return ListNotesResult(
            notes=[note_to_model(n) for n in results],
            total=len(results),
        )
