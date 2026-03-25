# Design: Reduce MCP Output Context Occupation

**Date:** 2026-03-25
**Status:** Approved
**Scope:** `models.py`, `tools/_helpers.py`, all tool modules, tests

---

## Problem

Every MCP tool call returns full `NoteInfo` objects with 14 fields each. For bulk queries like `list_notes` (which can return 10–20 notes), this generates significant JSON that occupies LLM context unnecessarily. Several fields are either never used by skill commands or only needed when inspecting a single note in detail.

Specific redundancies identified:
- `server_id` — always `null` in practice; only useful for low-level debugging
- `url` — Google Keep web link; skill commands never navigate to it in bulk
- `color` — rarely used; not needed in list views
- `LabelInfo.id` — skill commands only use `label.name`, never `label.id`
- `ToolResult.note` — mutation tools return the full note after every write; callers never read it
- `ListNotesResult.total` — always equals `len(notes)`; pure redundancy

---

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| LabelInfo fields | Keep `name` only, drop `id` | Skills never use label IDs |
| Low-frequency NoteInfo fields | Make Optional, omit via `exclude_none` in list context | Single model, minimal change |
| list vs get differentiation | `note_to_model(full=False)` for lists, `full=True` for `get_note` | Clear call-site intent |
| ToolResult.note | Remove entirely | Mutations only need success/message; callers use `get_note` if they need the note |
| ListNotesResult.total | Remove | Redundant with `len(notes)` |

---

## Section 1: Model Changes

### `LabelInfo`
```python
class LabelInfo(BaseModel):
    name: str  # removed: id: str
```

### `NoteInfo`
Low-frequency fields become `Optional` with default `None`. When serialized with `exclude_none=True`, absent fields produce no JSON output.

```python
class NoteInfo(BaseModel):
    # Always present (core fields)
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

    # Only populated in full/detail mode (get_note)
    server_id: str | None = None
    url: str | None = None
    color: str | None = None
```

### `ToolResult`
```python
class ToolResult(BaseModel):
    success: bool
    message: str
    # removed: note: NoteInfo | None = None
```

### `ListNotesResult`
```python
class ListNotesResult(BaseModel):
    notes: list[NoteInfo]
    # removed: total: int
```

---

## Section 2: Implementation Changes

### `tools/_helpers.py` — `note_to_model`

Add `full: bool = False` parameter:

```python
def note_to_model(note: gkeepapi.node.TopLevelNode, full: bool = False) -> NoteInfo:
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
        # Full mode only:
        server_id=note.server_id if full else None,
        url=note.url if full else None,
        color=note.color.value if full else None,
    )
```

### Call-site summary

| Tool | `full` | Change |
|------|--------|--------|
| `get_note` | `True` | Single detail view, return complete fields |
| `list_notes` | `False` (default) | Bulk list, strip low-frequency fields |
| `search_notes` | `False` (default) | Bulk list, strip low-frequency fields |
| All mutations (create, update, archive, pin, trash, etc.) | — | Remove `note=note_to_model(note)` entirely |

### `tools/labels.py` — `list_labels` call site

`list_labels` constructs `LabelInfo` directly (outside `note_to_model`):

```python
# Before:
labels=[LabelInfo(id=lbl.id, name=lbl.name) for lbl in all_labels]
# After:
labels=[LabelInfo(name=lbl.name) for lbl in all_labels]
```

This call site must be updated alongside the `LabelInfo` model change, or a Pydantic validation error will occur at runtime.

### `ListNotesResult` call sites in `notes.py` and `search.py`

Four explicit call sites pass `total=` and must be updated after `total` is removed from the model:

- `notes.py` line 35: `ListNotesResult(notes=[], total=0)` → `ListNotesResult(notes=[])`
- `notes.py` line 41: `ListNotesResult(notes=[], total=0)` → `ListNotesResult(notes=[])`
- `notes.py` line 50–53: `ListNotesResult(notes=[...], total=len(results))` → `ListNotesResult(notes=[...])`
- `search.py`: `ListNotesResult(notes=[...], total=len(results))` → `ListNotesResult(notes=[...])`

### `ListLabelsResult.total` — explicitly out of scope

`labels.py` defines `ListLabelsResult` with a `total` field exhibiting the same redundancy. Removing it is **out of scope** for this change to keep the diff focused. It can be addressed in a follow-up.

### Serialization

FastMCP serializes tool return values by calling `model_dump(mode="json", by_alias=True)` (confirmed in `mcp/server/fastmcp/utilities/func_metadata.py` line 129). It does **not** pass `exclude_none=True`, so `ConfigDict(exclude_none=True)` — which is a `model_dump` call-site option, not a valid `ConfigDict` key in Pydantic v2 — would have no effect.

The correct approach is to override serialization on `NoteInfo` using Pydantic v2's `@model_serializer`:

```python
from pydantic import BaseModel, model_serializer

class NoteInfo(BaseModel):
    # ... fields ...

    @model_serializer(mode="wrap")
    def _serialize(self, handler):
        data = handler(self)
        return {k: v for k, v in data.items() if v is not None}
```

This ensures `None` fields are stripped regardless of how `model_dump` is called, including FastMCP's internal call. **Note:** `items` for regular (non-list) notes will also be `None` and thus stripped — this is intentional and correct, since `items` is only meaningful for list-type notes.

**Important:** Add `from pydantic import model_serializer` to `models.py` imports (currently only `BaseModel` is imported).

---

## Section 3: Test Changes

### Existing tests to update

- **`ToolResult.note` assertions**: Remove all `result.note` checks; only assert `result.success` and `result.message`
- **`ListNotesResult.total` assertions**: Replace `result.total == N` with `len(result.notes) == N`
- **`LabelInfo.id` assertions**: Remove any `label.id` checks; assert only `label.name`
- **`test_note_to_model_color`** in `tests/test_notes.py`: This test calls `note_to_model(real_note)` without `full=True` and asserts `result.color == "RED"`. After the change, `color` will be `None` in slim mode. Update to `note_to_model(real_note, full=True)` to test full-mode behavior explicitly.

### New tests to add

1. **Slim mode** (`list_notes` / `search_notes`): Assert that returned `NoteInfo` objects have `server_id is None`, `url is None`, `color is None`
2. **Full mode** (`get_note`): Assert that returned `NoteInfo` has `server_id`, `url`, `color` populated with actual values
3. **Serialization**: Assert that slim-mode notes serialized to dict do not contain keys `server_id`, `url`, `color` (i.e., `exclude_none` is active)

### Unchanged
- `ListItemInfo` structure and all assertions on it
- Core `NoteInfo` field assertions (`id`, `title`, `text`, `labels`, `created`, `updated`, `items`)
- All `ToolResult.success` / `ToolResult.message` assertions

---

## Expected Impact

| Scenario | Before | After (estimate) |
|----------|--------|-----------------|
| `list_notes` returning 13 notes | ~4,500 chars | ~2,800 chars (~38% reduction) |
| `get_note` single note | ~350 chars | ~350 chars (unchanged) |
| Mutation (e.g. `add_label_to_note`) | `{success, message, note: {...}}` | `{success, message}` |
