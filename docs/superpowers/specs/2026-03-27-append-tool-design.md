# Design: append_text for update_note

Date: 2026-03-27

## Problem

Updating a note's body currently requires three steps from the caller:

1. `get_note` — fetch full text (token cost)
2. Client-side concatenation — construct the new full body
3. `update_note` — write the full body back (token cost)

The concatenation step belongs on the server. Moving it there eliminates the `get_note` round-trip and reduces token consumption.

## Scope

Text notes (`gkeepapi.node.Note`) only. List notes (`gkeepapi.node.List`) are out of scope — their equivalent is `update_list_items(add_items=...)`.

## Solution

Extend the existing `update_note` tool with one new optional parameter: `append_text`.

### Interface

```python
def update_note(
    note_id: str,
    title: str | None = None,
    text: str | None = None,
    append_text: str | None = None,   # NEW
    pinned: bool | None = None,
    archived: bool | None = None,
    color: str | None = None,
) -> ToolResult:
```

### Behaviour

- `text` and `append_text` are **mutually exclusive**. If both are provided, return `ToolResult(success=False, message="'text' and 'append_text' are mutually exclusive")` immediately, before any other processing.
- When `append_text` is provided on a list note, return the same error as `text` on a list: `"Note {id} is a list; use update_list_items to modify items"`.
- Append logic:
  - If `note.text` is non-empty: `note.text = note.text + "\n" + append_text`
  - If `note.text` is empty: `note.text = append_text` (no leading newline)

### Docstring addition

```
append_text: Text to append to the end of the note body (mutually exclusive with text).
             A newline is inserted between existing content and the new text.
             If the note is empty, the text is set directly without a leading newline.
```

## Files Changed

| File | Change |
|------|--------|
| `src/google_keep_mcp/tools/notes.py` | Add `append_text` parameter and logic to `update_note` |
| `tests/test_notes.py` | Add 3 new test cases |

## Tests

Three new test cases in `tests/test_notes.py`, following existing style (real `gkeepapi.node.*` objects, `monkeypatch` on `_state._keep`):

1. **`test_append_note_adds_newline`** — non-empty body: result is `"original\nnew content"`
2. **`test_append_note_empty_body`** — empty body: result is `"new content"` (no leading newline)
3. **`test_append_note_mutually_exclusive_with_text`** — both `text` and `append_text` provided: returns `success=False`

No new test for list-type rejection — the existing code path is already covered by the list rejection test for `text`.

## Non-Goals

- `prepend_text` — not needed now (YAGNI)
- A separate `append_note` tool — would duplicate `update_note` for no benefit
- List note append — semantically covered by `update_list_items`
