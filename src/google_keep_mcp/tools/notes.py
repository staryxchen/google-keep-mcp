from __future__ import annotations
import gkeepapi
from mcp.server.fastmcp import FastMCP

from ..models import NoteInfo, ToolResult, ListNotesResult
from .._state import get_keep
from ._helpers import note_to_model


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def list_notes(
        archived: bool = False,
        trashed: bool = False,
        pinned: bool | None = None,
        color: str | None = None,
        label: str | None = None,
    ) -> ListNotesResult:
        """List all notes with optional filters.

        Args:
            archived: If True, return only archived notes. Default False returns non-archived.
            trashed: If True, return only trashed notes.
            pinned: If True/False, filter by pinned state. If None, return all.
            color: Filter by color name (e.g. "RED", "BLUE", "DEFAULT").
            label: Filter by label name (case-insensitive).
        """
        keep = get_keep()
        colors = None
        if color is not None:
            try:
                colors = [gkeepapi.node.ColorValue(color.upper())]
            except ValueError:
                return ListNotesResult(notes=[], total=0)

        label_obj = None
        if label is not None:
            label_obj = keep.findLabel(label)
            if label_obj is None:
                return ListNotesResult(notes=[], total=0)

        results = list(keep.find(
            archived=archived,
            trashed=trashed,
            pinned=pinned,
            colors=colors,
            labels=[label_obj] if label_obj else None,
        ))
        return ListNotesResult(
            notes=[note_to_model(n) for n in results],
            total=len(results),
        )

    @mcp.tool()
    def get_note(note_id: str) -> NoteInfo | None:
        """Get a specific note by its local ID.

        Args:
            note_id: The note's local ID.
        """
        keep = get_keep()
        note = keep.get(note_id)
        if note is None:
            return None
        return note_to_model(note)

    @mcp.tool()
    def create_note(title: str = "", text: str = "") -> ToolResult:
        """Create a new text note.

        Args:
            title: Title of the note (can be empty).
            text: Body text of the note.
        """
        keep = get_keep()
        note = keep.createNote(title=title or None, text=text or None)
        keep.sync()
        return ToolResult(
            success=True,
            message=f"Note created with ID {note.id}",
            note=note_to_model(note),
        )

    @mcp.tool()
    def update_note(
        note_id: str,
        title: str | None = None,
        text: str | None = None,
        pinned: bool | None = None,
        archived: bool | None = None,
        color: str | None = None,
    ) -> ToolResult:
        """Update an existing note's content or properties.

        Args:
            note_id: The note ID to update.
            title: New title (None = no change).
            text: New text content (None = no change). Not applicable to lists.
            pinned: Set pinned state (None = no change).
            archived: Set archived state (None = no change).
            color: Set color by name e.g. "RED", "GREEN", "DEFAULT" (None = no change).
        """
        keep = get_keep()
        note = keep.get(note_id)
        if note is None:
            return ToolResult(success=False, message=f"Note {note_id} not found")
        if title is not None:
            note.title = title
        if text is not None:
            if isinstance(note, gkeepapi.node.Note):
                note.text = text
            else:
                return ToolResult(success=False, message=f"Note {note_id} is a list; use update_list_items to modify items")
        if pinned is not None:
            note.pinned = pinned
        if archived is not None:
            note.archived = archived
        if color is not None:
            try:
                note.color = gkeepapi.node.ColorValue(color.upper())
            except ValueError:
                return ToolResult(success=False, message=f"Invalid color '{color}'. Valid values: DEFAULT, RED, PINK, YELLOW, BLUE, GRAY, TEAL, GREEN, CERULEAN, PURPLE, WHITE, BROWN, ORANGE, LIGHT_PINK, LIGHTSKYBLUE, MEMO")
        keep.sync()
        return ToolResult(
            success=True,
            message=f"Note {note_id} updated",
            note=note_to_model(note),
        )

    @mcp.tool()
    def delete_note(note_id: str) -> ToolResult:
        """Trash a note (moves to trash, does not permanently delete).

        Args:
            note_id: The note ID to trash.
        """
        keep = get_keep()
        note = keep.get(note_id)
        if note is None:
            return ToolResult(success=False, message=f"Note {note_id} not found")
        note.trash()
        keep.sync()
        return ToolResult(success=True, message=f"Note {note_id} moved to trash")

    @mcp.tool()
    def untrash_note(note_id: str) -> ToolResult:
        """Restore a note from trash.

        Args:
            note_id: The note ID to restore.
        """
        keep = get_keep()
        note = keep.get(note_id)
        if note is None:
            return ToolResult(success=False, message=f"Note {note_id} not found")
        if not note.trashed:
            return ToolResult(success=False, message=f"Note {note_id} is not in trash")
        note.untrash()
        keep.sync()
        return ToolResult(success=True, message=f"Note {note_id} restored from trash", note=note_to_model(note))

    @mcp.tool()
    def archive_note(note_id: str, archived: bool = True) -> ToolResult:
        """Archive or unarchive a note.

        Args:
            note_id: The note ID.
            archived: True to archive, False to unarchive.
        """
        keep = get_keep()
        note = keep.get(note_id)
        if note is None:
            return ToolResult(success=False, message=f"Note {note_id} not found")
        note.archived = archived
        keep.sync()
        action = "archived" if archived else "unarchived"
        return ToolResult(success=True, message=f"Note {note_id} {action}", note=note_to_model(note))

    @mcp.tool()
    def pin_note(note_id: str, pinned: bool = True) -> ToolResult:
        """Pin or unpin a note.

        Args:
            note_id: The note ID.
            pinned: True to pin, False to unpin.
        """
        keep = get_keep()
        note = keep.get(note_id)
        if note is None:
            return ToolResult(success=False, message=f"Note {note_id} not found")
        note.pinned = pinned
        keep.sync()
        action = "pinned" if pinned else "unpinned"
        return ToolResult(success=True, message=f"Note {note_id} {action}", note=note_to_model(note))
