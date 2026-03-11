# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install (requires uv)
uv pip install -e ".[dev]"

# Run all tests
.venv/bin/python3 -m pytest tests/ -v

# Run a single test file
.venv/bin/python3 -m pytest tests/test_notes.py -v

# Run a single test by name
.venv/bin/python3 -m pytest tests/test_notes.py::test_create_note_syncs -v

# Run the server (requires .env with credentials)
.venv/bin/google-keep-mcp

# Inspect tools interactively
.venv/bin/mcp dev src/google_keep_mcp/server.py
```

No linter is configured; the project uses standard Python conventions.

## Architecture

The server is a **stdio MCP server** built on `FastMCP`. Authentication happens once at startup inside the `lifespan` async context manager in `server.py`; the authenticated `gkeepapi.Keep` instance is stored as a module-level singleton.

### Circular import avoidance

`server.py` imports the tool modules, and tool modules need access to the `Keep` client — this would create a circular import if tools imported from `server.py`. The solution is `_state.py`, which holds `_keep` and `get_keep()`. Tools import from `_state`; `server.py` imports from `_state` separately. Tool modules are imported in `server.py` **after** `mcp` is defined (with a `# noqa: E402` comment).

### Adding a new tool

Each tool domain has its own module under `src/google_keep_mcp/tools/`. Each module exposes a single `register(mcp: FastMCP) -> None` function that uses `@mcp.tool()` decorators internally. To add a tool:

1. Add a decorated function inside the appropriate `register()` in `tools/*.py`
2. Use `get_keep()` from `_state` to get the Keep client
3. Return a Pydantic model from `models.py` (or a new model defined in `models.py`)
4. Call `keep.sync()` after any mutation

### Key design choices

- **`ToolResult(success=False, message=...)`** is returned for domain errors (note not found, wrong type, duplicate label). Exceptions are only raised for infrastructure failures (auth errors, network).
- **`note.trash()`** is used for deletion — gkeepapi has no hard-delete API.
- **`keep.sync()`** is called after every mutation. gkeepapi performs incremental sync (only dirty nodes), so this is one HTTP request per mutation.
- Tests mock `gkeepapi.Keep` via `monkeypatch` on `_state._keep` (in `conftest.py`), but use **real** `gkeepapi.node.*` objects for behavioral assertions.

## Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `GOOGLE_EMAIL` | Yes | Google account email |
| `GOOGLE_MASTER_TOKEN` | Yes | Master token (not password) — obtain via `gpsoauth` |
| `KEEP_CACHE_FILE` | No | Path to JSON cache; enables incremental sync on restart |
| `LOG_LEVEL` | No | `DEBUG`/`INFO`/`WARNING`/`ERROR` (default `INFO`) |

## Skill commands sync rule

The project maintains custom skill commands under `.claude/commands/`. When any file in that directory is added, removed, or modified, **immediately sync the changes to `~/.claude/commands/`** (global commands directory) by copying the updated files. This ensures the commands are available across all projects.

## Git conventions

All commits include:
```
Signed-off-by: staryxchen <staryxchen@tencent.com>
Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```
