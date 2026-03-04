from __future__ import annotations
import gkeepapi
from ..models import NoteInfo, LabelInfo, ListItemInfo


def note_to_model(note: gkeepapi.node.TopLevelNode) -> NoteInfo:
    """Convert a gkeepapi node to a NoteInfo Pydantic model."""
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
        server_id=note.server_id,
        type="list" if is_list else "note",
        title=note.title,
        text=note.text,
        pinned=note.pinned,
        archived=note.archived,
        trashed=note.trashed,
        color=note.color.value,
        labels=[
            LabelInfo(id=lbl.id, name=lbl.name)
            for lbl in note.labels.all()
        ],
        url=note.url,
        created=note.timestamps.created.isoformat(),
        updated=note.timestamps.updated.isoformat(),
        items=items,
    )
