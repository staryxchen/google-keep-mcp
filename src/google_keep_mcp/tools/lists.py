from __future__ import annotations
from typing import Any
import gkeepapi
from mcp.server.fastmcp import FastMCP

from ..models import ToolResult
from .._state import get_keep
from ._helpers import note_to_model


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def create_list(
        title: str = "",
        items: list[dict[str, Any]] | None = None,
    ) -> ToolResult:
        """Create a new checklist.

        Args:
            title: Title of the list.
            items: Optional list of items. Each item is a dict with keys:
                   - "text" (str, required): Item text
                   - "checked" (bool, optional, default False): Checked state
        """
        keep = get_keep()
        item_tuples: list[tuple[str, bool]] = []
        if items:
            for item in items:
                text = item.get("text", "")
                checked = bool(item.get("checked", False))
                item_tuples.append((text, checked))
        node = keep.createList(title=title or None, items=item_tuples)
        keep.sync()
        return ToolResult(
            success=True,
            message=f"List created with ID {node.id}",
            note=note_to_model(node),
        )

    @mcp.tool()
    def update_list_items(
        note_id: str,
        add_items: list[dict[str, Any]] | None = None,
        update_items: list[dict[str, Any]] | None = None,
        check_all: bool = False,
        uncheck_all: bool = False,
    ) -> ToolResult:
        """Add, update, or toggle items in a checklist.

        Args:
            note_id: The list note ID.
            add_items: Items to add. Each is a dict with "text" (str) and optional "checked" (bool).
            update_items: Items to update. Each is a dict with "id" (list item ID),
                          and optionally "text" and/or "checked" to change.
            check_all: If True, mark all items as checked.
            uncheck_all: If True, mark all items as unchecked.
        """
        keep = get_keep()
        note = keep.get(note_id)
        if note is None:
            return ToolResult(success=False, message=f"Note {note_id} not found")
        if not isinstance(note, gkeepapi.node.List):
            return ToolResult(success=False, message=f"Note {note_id} is not a list")

        if add_items:
            for item in add_items:
                note.add(
                    text=item.get("text", ""),
                    checked=bool(item.get("checked", False)),
                )

        if update_items:
            item_map = {li.id: li for li in note.items}
            for update in update_items:
                item_id = update.get("id")
                if item_id and item_id in item_map:
                    li = item_map[item_id]
                    if "text" in update:
                        li.text = update["text"]
                    if "checked" in update:
                        li.checked = bool(update["checked"])

        if check_all:
            for li in note.items:
                li.checked = True
        elif uncheck_all:
            for li in note.items:
                li.checked = False

        keep.sync()
        return ToolResult(
            success=True,
            message=f"List {note_id} updated",
            note=note_to_model(note),
        )

    @mcp.tool()
    def sort_list_items(note_id: str, reverse: bool = False) -> ToolResult:
        """Sort checklist items alphabetically.

        Args:
            note_id: The list note ID.
            reverse: If True, sort in reverse (Z→A). Default False (A→Z).
        """
        keep = get_keep()
        note = keep.get(note_id)
        if note is None:
            return ToolResult(success=False, message=f"Note {note_id} not found")
        if not isinstance(note, gkeepapi.node.List):
            return ToolResult(success=False, message=f"Note {note_id} is not a list")
        note.sort_items(reverse=reverse)
        keep.sync()
        order = "Z→A" if reverse else "A→Z"
        return ToolResult(
            success=True,
            message=f"List {note_id} items sorted {order}",
            note=note_to_model(note),
        )
