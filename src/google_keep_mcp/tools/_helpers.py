from __future__ import annotations

import gkeepapi

from ..models import LabelInfo, ListItemInfo, NoteInfo


def note_to_model(note: gkeepapi.node.TopLevelNode, full: bool = False) -> NoteInfo:
    """Convert a gkeepapi node to a NoteInfo Pydantic model.

    Args:
        note: The gkeepapi node to convert.
        full: If True, populate detail fields (server_id, url, color).
              Use True only for get_note (single-item detail view).
              Defaults to False for bulk list/search results.
    """
    is_list = isinstance(note, gkeepapi.node.List)
    items = None
    if is_list:
        items = [
            ListItemInfo(
                id=li.id,
                text=li.text,
                checked=li.checked,
                indented=li.indented,
            )
            for li in note.items
        ]

    return NoteInfo(
        id=note.id,
        type="list" if is_list else "note",
        title=note.title,
        text=note.text,
        pinned=note.pinned,
        archived=note.archived,
        trashed=note.trashed,
        labels=[LabelInfo(name=lbl.name) for lbl in note.labels.all()],
        created=note.timestamps.created.isoformat(),
        updated=note.timestamps.updated.isoformat(),
        items=items,
        # Detail fields: only populated in full mode
        server_id=note.server_id if full else None,
        url=note.url if full else None,
        color=note.color.value if full else None,
    )
