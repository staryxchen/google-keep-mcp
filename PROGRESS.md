# Implementation Progress

## Status

| Tool | Implemented | Tests | Notes |
|------|-------------|-------|-------|
| `list_notes` | ✅ | ✅ | Filters: archived, trashed, pinned, color, label |
| `get_note` | ✅ | ✅ | |
| `create_note` | ✅ | ✅ | |
| `update_note` | ✅ | ✅ | |
| `delete_note` | ✅ | ✅ | Uses `trash()`, not hard delete |
| `archive_note` | ✅ | ✅ | |
| `pin_note` | ✅ | ✅ | |
| `create_list` | ✅ | ✅ | |
| `update_list_items` | ✅ | ✅ | add, update by ID, check_all, uncheck_all |
| `search_notes` | ✅ | ✅ | |
| `list_labels` | ✅ | ✅ | |
| `create_label` | ✅ | ✅ | Checks for duplicates |
| `add_label_to_note` | ✅ | ✅ | |

## Implementation Notes

### Authentication
- Uses `keep.authenticate(email, master_token)` (preferred over deprecated `login`)
- Master token must be obtained separately via `gpsoauth`
- On startup: full sync if no cache, incremental sync if cache exists

### Sync Strategy
- Full sync on server startup (via `authenticate()` default)
- Incremental sync via `keep.sync()` after every mutation
- Optional state cache via `keep.dump()`/`keep.restore()` for faster restarts
  - Configure with `KEEP_CACHE_FILE` env var

### Architecture
- `_state.py`: singleton `_keep` and `get_keep()` to avoid circular imports
- `server.py`: FastMCP instance + lifespan (auth) + tool registration
- `tools/`: one module per domain (notes, lists, search, labels)
- `models.py`: shared Pydantic output types
- `tools/_helpers.py`: `note_to_model()` converter

## Changelog

### 2026-03-04
- Project initialized
- All 13 tools implemented and tested
- 23 unit tests passing
