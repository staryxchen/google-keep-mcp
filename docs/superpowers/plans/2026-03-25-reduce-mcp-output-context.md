# Reduce MCP Output Context Occupation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce JSON output size of MCP tools by removing unused fields, introducing slim/full mode for NoteInfo, and stripping ToolResult.note from mutations.

**Architecture:** Single conversion point `note_to_model(full=False)` in `_helpers.py` controls which fields are populated. `@model_serializer` on `NoteInfo` strips `None` fields before FastMCP serializes. Mutations return only `success` + `message`.

**Tech Stack:** Python 3.11, Pydantic v2 (`model_serializer`), FastMCP, gkeepapi, pytest

**Spec:** `docs/superpowers/specs/2026-03-25-reduce-mcp-output-context-design.md`

---

## File Map

| File | Action | What changes |
|------|--------|-------------|
| `src/google_keep_mcp/models.py` | Modify | Remove `LabelInfo.id`, make `NoteInfo` optional fields + `@model_serializer`, remove `ToolResult.note`, remove `ListNotesResult.total` |
| `src/google_keep_mcp/tools/_helpers.py` | Modify | Add `full: bool = False` param to `note_to_model` |
| `src/google_keep_mcp/tools/notes.py` | Modify | `get_note` passes `full=True`; remove `note=` from all mutation returns; fix 3 `ListNotesResult` call sites |
| `src/google_keep_mcp/tools/search.py` | Modify | Fix 1 `ListNotesResult` call site |
| `src/google_keep_mcp/tools/lists.py` | Modify | Remove `note=` from 3 mutation returns |
| `src/google_keep_mcp/tools/labels.py` | Modify | Fix `LabelInfo(id=..., name=...)` call site |
| `tests/test_notes.py` | Modify + extend | Fix `test_note_to_model_color`; add slim/full/serialization tests |

---

## Task 1: Update models.py — LabelInfo, ToolResult, ListNotesResult

**Files:**
- Modify: `src/google_keep_mcp/models.py`
- Test: `tests/test_notes.py` (run existing suite to verify no breakage yet)

- [ ] **Step 1: Write the failing tests for removed fields**

Add to `tests/test_notes.py`:

```python
def test_label_info_has_no_id():
    from google_keep_mcp.models import LabelInfo
    lbl = LabelInfo(name="Work")
    assert lbl.name == "Work"
    assert not hasattr(lbl, "id")


def test_tool_result_has_no_note_field():
    from google_keep_mcp.models import ToolResult
    result = ToolResult(success=True, message="ok")
    assert result.success is True
    assert not hasattr(result, "note")


def test_list_notes_result_has_no_total():
    from google_keep_mcp.models import ListNotesResult
    result = ListNotesResult(notes=[])
    assert result.notes == []
    assert not hasattr(result, "total")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /data/workspace/google-keep-mcp
.venv/bin/python3 -m pytest tests/test_notes.py::test_label_info_has_no_id tests/test_notes.py::test_tool_result_has_no_note_field tests/test_notes.py::test_list_notes_result_has_no_total -v
```

Expected: all 3 FAIL

- [ ] **Step 3: Update models.py**

Replace the entire content of `src/google_keep_mcp/models.py`:

```python
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
```

- [ ] **Step 4: Run the 3 new tests to verify they pass**

```bash
.venv/bin/python3 -m pytest tests/test_notes.py::test_label_info_has_no_id tests/test_notes.py::test_tool_result_has_no_note_field tests/test_notes.py::test_list_notes_result_has_no_total -v
```

Expected: all 3 PASS

- [ ] **Step 5: Run full suite to see which existing tests now break**

```bash
.venv/bin/python3 -m pytest tests/ -v 2>&1 | tail -30
```

Expected: several failures — call sites still use removed fields. That's expected; we'll fix them in the next tasks.

- [ ] **Step 6: Commit**

```bash
git add src/google_keep_mcp/models.py tests/test_notes.py
git commit -m "$(cat <<'EOF'
refactor(models): slim down LabelInfo, ToolResult, ListNotesResult

- LabelInfo: remove id field (name is all callers need)
- NoteInfo: make server_id/url/color Optional; add @model_serializer
  to strip None fields from FastMCP output
- ToolResult: remove note field (mutations return success+message only)
- ListNotesResult: remove total field (redundant with len(notes))

Signed-off-by: staryxchen <staryxchen@tencent.com>
EOF
)"
```

---

## Task 2: Update _helpers.py — add full parameter

**Files:**
- Modify: `src/google_keep_mcp/tools/_helpers.py`
- Test: `tests/test_notes.py`

- [ ] **Step 1: Write failing tests for slim/full mode**

Add to `tests/test_notes.py`:

```python
def test_note_to_model_slim_omits_detail_fields(real_note):
    """Slim mode (default): server_id, url, color are None."""
    result = note_to_model(real_note)
    assert result.server_id is None
    assert result.url is None
    assert result.color is None


def test_note_to_model_full_includes_detail_fields(real_note):
    """Full mode: server_id, url, color are populated."""
    import gkeepapi.node as gnode
    real_note.color = gnode.ColorValue.Red
    result = note_to_model(real_note, full=True)
    assert result.color == "RED"
    # url and server_id may be empty strings but are not None
    assert result.url is not None
    assert result.server_id is not None


def test_note_to_model_slim_serializes_without_detail_keys(real_note):
    """Slim mode serialization: None fields absent from dict output."""
    result = note_to_model(real_note)
    data = result.model_dump(mode="json")
    assert "server_id" not in data
    assert "url" not in data
    assert "color" not in data
```

Also update the existing broken `test_note_to_model_color`:

```python
def test_note_to_model_color(real_note):
    real_note.color = gnode.ColorValue.Red
    result = note_to_model(real_note, full=True)  # full=True to get color
    assert result.color == "RED"
```

- [ ] **Step 2: Run new tests to verify they fail**

```bash
.venv/bin/python3 -m pytest \
  tests/test_notes.py::test_note_to_model_slim_omits_detail_fields \
  tests/test_notes.py::test_note_to_model_full_includes_detail_fields \
  tests/test_notes.py::test_note_to_model_slim_serializes_without_detail_keys \
  tests/test_notes.py::test_note_to_model_color \
  -v
```

Expected: all 4 FAIL (`note_to_model` doesn't accept `full` yet; `test_note_to_model_color` now calls it with `full=True`)

- [ ] **Step 3: Update _helpers.py**

Replace the entire content of `src/google_keep_mcp/tools/_helpers.py`:

```python
from __future__ import annotations
import gkeepapi
from ..models import NoteInfo, LabelInfo, ListItemInfo


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
```

- [ ] **Step 4: Run the new tests to verify they pass**

```bash
.venv/bin/python3 -m pytest \
  tests/test_notes.py::test_note_to_model_slim_omits_detail_fields \
  tests/test_notes.py::test_note_to_model_full_includes_detail_fields \
  tests/test_notes.py::test_note_to_model_slim_serializes_without_detail_keys \
  tests/test_notes.py::test_note_to_model_color \
  -v
```

Expected: all 4 PASS

- [ ] **Step 5: Commit**

```bash
git add src/google_keep_mcp/tools/_helpers.py tests/test_notes.py
git commit -m "$(cat <<'EOF'
refactor(_helpers): add full=False param to note_to_model

- Default slim mode omits server_id, url, color (None → stripped by serializer)
- full=True for get_note detail view: populates all fields
- LabelInfo construction updated: LabelInfo(name=...) only

Signed-off-by: staryxchen <staryxchen@tencent.com>
EOF
)"
```

---

## Task 3: Fix call sites — notes.py

**Files:**
- Modify: `src/google_keep_mcp/tools/notes.py`

- [ ] **Step 1: Update notes.py**

Apply the following changes to `src/google_keep_mcp/tools/notes.py`:

**`get_note`** — pass `full=True`:
```python
    @mcp.tool()
    def get_note(note_id: str) -> NoteInfo | None:
        keep = get_keep()
        note = keep.get(note_id)
        if note is None:
            return None
        return note_to_model(note, full=True)  # full=True: detail view
```

**`list_notes`** — fix 3 call sites (remove `total=`):
```python
        if color is not None:
            try:
                colors = [gkeepapi.node.ColorValue(color.upper())]
            except ValueError:
                return ListNotesResult(notes=[])   # was: notes=[], total=0

        label_obj = None
        if label is not None:
            label_obj = keep.findLabel(label)
            if label_obj is None:
                return ListNotesResult(notes=[])   # was: notes=[], total=0

        results = list(keep.find(...))
        return ListNotesResult(
            notes=[note_to_model(n) for n in results],
            # removed: total=len(results)
        )
```

**All mutation tools** (`create_note`, `update_note`, `untrash_note`, `archive_note`, `pin_note`) — remove `note=note_to_model(note)`:
```python
        return ToolResult(success=True, message=f"Note created with ID {note.id}")
        return ToolResult(success=True, message=f"Note {note_id} updated")
        return ToolResult(success=True, message=f"Note {note_id} restored from trash")
        return ToolResult(success=True, message=f"Note {note_id} {action}")   # archive
        return ToolResult(success=True, message=f"Note {note_id} {action}")   # pin
```

(`delete_note` already returns no note.)

- [ ] **Step 2: Run the full test suite**

```bash
.venv/bin/python3 -m pytest tests/ -v 2>&1 | tail -30
```

Expected: remaining failures are in `search.py` and `lists.py` call sites only.

- [ ] **Step 3: Commit**

```bash
git add src/google_keep_mcp/tools/notes.py
git commit -m "$(cat <<'EOF'
fix(notes): update call sites for slimmed models

- get_note: pass full=True to note_to_model
- list_notes: remove total= from ListNotesResult construction
- mutations: remove note= from ToolResult returns

Signed-off-by: staryxchen <staryxchen@tencent.com>
EOF
)"
```

---

## Task 4: Fix call sites — search.py and lists.py

**Files:**
- Modify: `src/google_keep_mcp/tools/search.py`
- Modify: `src/google_keep_mcp/tools/lists.py`

- [ ] **Step 1: Update search.py** — remove `total=len(results)`:

```python
        return ListNotesResult(
            notes=[note_to_model(n) for n in results],
            # removed: total=len(results)
        )
```

- [ ] **Step 2: Update lists.py** — remove `note=note_to_model(node/note)` from all 3 mutations:

`create_list`:
```python
        return ToolResult(
            success=True,
            message=f"List created with ID {node.id}",
            # removed: note=note_to_model(node)
        )
```

`update_list_items`:
```python
        return ToolResult(
            success=True,
            message=f"List {note_id} updated",
            # removed: note=note_to_model(note)
        )
```

`sort_list_items`:
```python
        return ToolResult(
            success=True,
            message=f"List {note_id} items sorted {order}",
            # removed: note=note_to_model(note)
        )
```

- [ ] **Step 3: Run the full test suite — expect all green**

```bash
.venv/bin/python3 -m pytest tests/ -v
```

Expected: ALL PASS

- [ ] **Step 4: Commit**

```bash
git add src/google_keep_mcp/tools/search.py src/google_keep_mcp/tools/lists.py
git commit -m "$(cat <<'EOF'
fix(search,lists): update call sites for slimmed models

- search.py: remove total= from ListNotesResult
- lists.py: remove note= from all 3 ToolResult returns

Signed-off-by: staryxchen <staryxchen@tencent.com>
EOF
)"
```

---

## Task 5: Fix call site — labels.py

**Files:**
- Modify: `src/google_keep_mcp/tools/labels.py`

- [ ] **Step 1: Update labels.py** — fix the `LabelInfo` construction in `list_labels`:

```python
        return ListLabelsResult(
            labels=[LabelInfo(name=lbl.name) for lbl in all_labels],  # removed: id=lbl.id
            total=len(all_labels),
        )
```

- [ ] **Step 2: Run full test suite**

```bash
.venv/bin/python3 -m pytest tests/ -v
```

Expected: ALL PASS

- [ ] **Step 3: Commit**

```bash
git add src/google_keep_mcp/tools/labels.py
git commit -m "$(cat <<'EOF'
fix(labels): remove LabelInfo id= from list_labels call site

LabelInfo.id was removed from the model; update the one call
site outside note_to_model that constructed LabelInfo directly.

Signed-off-by: staryxchen <staryxchen@tencent.com>
EOF
)"
```

---

## Task 6: Final verification

- [ ] **Step 1: Run full test suite one last time**

```bash
.venv/bin/python3 -m pytest tests/ -v
```

Expected: ALL PASS, no warnings about unexpected keyword arguments

- [ ] **Step 2: Smoke-test serialization manually**

```bash
.venv/bin/python3 - <<'EOF'
import gkeepapi.node as gnode
from google_keep_mcp.tools._helpers import note_to_model

# Slim mode — list context
note = gnode.Note()
note.title = "Test"
note.text = "Body"
slim = note_to_model(note, full=False)
d = slim.model_dump(mode="json")
assert "server_id" not in d, f"server_id leaked: {d}"
assert "url" not in d, f"url leaked: {d}"
assert "color" not in d, f"color leaked: {d}"
assert "items" not in d, f"items leaked for regular note: {d}"
print("Slim note keys:", sorted(d.keys()))

# Full mode — get_note context
full = note_to_model(note, full=True)
d2 = full.model_dump(mode="json")
assert "url" in d2, "url missing in full mode"
print("Full note keys:", sorted(d2.keys()))

print("All assertions passed.")
EOF
```

Expected output:
```
Slim note keys: ['archived', 'created', 'id', 'labels', 'pinned', 'text', 'title', 'trashed', 'type', 'updated']
Full note keys: ['archived', 'color', 'created', 'id', 'labels', 'pinned', 'server_id', 'text', 'title', 'trashed', 'type', 'updated', 'url']
All assertions passed.
```

- [ ] **Step 3: Update Google Keep note with progress**

```bash
# Use /progress skill to record completion in Google Keep note 19d1e032fa6.23840e44a36aa926
```
