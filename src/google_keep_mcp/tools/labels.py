from __future__ import annotations
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP

from ..models import LabelInfo, ToolResult
from .._state import get_keep


class ListLabelsResult(BaseModel):
    labels: list[LabelInfo]
    total: int


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def list_labels() -> ListLabelsResult:
        """List all labels in the Keep account."""
        keep = get_keep()
        all_labels = list(keep.labels())
        return ListLabelsResult(
            labels=[LabelInfo(id=lbl.id, name=lbl.name) for lbl in all_labels],
            total=len(all_labels),
        )

    @mcp.tool()
    def create_label(name: str) -> ToolResult:
        """Create a new label.

        Args:
            name: The label name (must be unique).
        """
        keep = get_keep()
        existing = keep.findLabel(name)
        if existing:
            return ToolResult(
                success=False,
                message=f"Label '{name}' already exists with ID {existing.id}",
            )
        label = keep.createLabel(name)
        keep.sync()
        return ToolResult(
            success=True,
            message=f"Label '{name}' created with ID {label.id}",
        )

    @mcp.tool()
    def add_label_to_note(note_id: str, label_name: str) -> ToolResult:
        """Apply a label to a note by label name.

        Args:
            note_id: The note ID to label.
            label_name: The name of the label to apply (case-insensitive).
        """
        keep = get_keep()
        note = keep.get(note_id)
        if note is None:
            return ToolResult(success=False, message=f"Note {note_id} not found")
        label = keep.findLabel(label_name)
        if label is None:
            return ToolResult(
                success=False,
                message=f"Label '{label_name}' not found. Use create_label first.",
            )
        note.labels.add(label)
        keep.sync()
        return ToolResult(
            success=True,
            message=f"Label '{label_name}' added to note {note_id}",
        )
