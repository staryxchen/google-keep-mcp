from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, model_serializer


class LabelInfo(BaseModel):
    name: str


class ListItemInfo(BaseModel):
    id: str
    text: str
    checked: bool
    indented: bool


class NoteInfo(BaseModel):
    # Core fields — always present
    id: str
    type: Literal["note", "list"]
    title: str
    text: str
    pinned: bool
    archived: bool
    trashed: bool
    labels: list[LabelInfo]
    created: str
    updated: str
    items: list[ListItemInfo] | None = None

    # Detail fields — only populated by get_note (full=True)
    server_id: str | None = None
    url: str | None = None
    color: str | None = None

    @model_serializer(mode="wrap")
    def _serialize(self, handler):
        data = handler(self)
        return {k: v for k, v in data.items() if v is not None}


class ToolResult(BaseModel):
    success: bool
    message: str


class ListNotesResult(BaseModel):
    notes: list[NoteInfo]
