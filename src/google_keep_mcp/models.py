from __future__ import annotations
from typing import Literal
from pydantic import BaseModel


class LabelInfo(BaseModel):
    id: str
    name: str


class ListItemInfo(BaseModel):
    id: str
    text: str
    checked: bool
    indented: bool


class NoteInfo(BaseModel):
    id: str
    server_id: str | None
    type: Literal["note", "list"]
    title: str
    text: str
    pinned: bool
    archived: bool
    trashed: bool
    color: str
    labels: list[LabelInfo]
    url: str
    created: str
    updated: str
    items: list[ListItemInfo] | None = None


class ToolResult(BaseModel):
    success: bool
    message: str
    note: NoteInfo | None = None


class ListNotesResult(BaseModel):
    notes: list[NoteInfo]
    total: int
