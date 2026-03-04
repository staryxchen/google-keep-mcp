# Google Keep MCP Server

An MCP (Model Context Protocol) server that wraps [gkeepapi](https://github.com/kiwiz/gkeepapi) to give AI assistants structured access to Google Keep notes, lists, and labels.

## Features

- **13 MCP tools** covering notes, checklists, labels, search, and note properties
- Token-based authentication (no deprecated password login)
- Optional state caching for faster restarts
- Structured Pydantic output models for all tools

## Requirements

- Python 3.11+
- A Google account with Keep access
- A Google master token (see below)

## Getting a Master Token

Google deprecated direct password authentication. You must obtain a master token once using `gpsoauth`:

```bash
pip install gpsoauth
```

```python
import gpsoauth

# Run this once on a machine where you can complete browser verification
result = gpsoauth.perform_master_login(
    "your@gmail.com",
    "your-password",
    "android-device-id",  # any string, e.g. "my-laptop"
)
print(result.get("Token"))  # Save this as GOOGLE_MASTER_TOKEN
```

If Google requires 2-step verification, a URL will be printed — visit it in a browser, approve the login, then re-run the script.

## Installation

```bash
git clone <repo-url>
cd google-keep-mcp
uv pip install -e .
```

Or install directly with pip:

```bash
pip install -e .
```

## Configuration

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_EMAIL` | Yes | Your Google account email |
| `GOOGLE_MASTER_TOKEN` | Yes | Master token from gpsoauth |
| `KEEP_CACHE_FILE` | No | Path to JSON cache for faster restarts |
| `LOG_LEVEL` | No | `DEBUG`, `INFO`, `WARNING`, `ERROR` (default: `INFO`) |

## Running

```bash
GOOGLE_EMAIL=you@gmail.com GOOGLE_MASTER_TOKEN=aas_et/... google-keep-mcp
```

Or with a `.env` file in the current directory:

```bash
google-keep-mcp
```

## Claude Desktop Integration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "google-keep": {
      "command": "/path/to/google-keep-mcp/.venv/bin/google-keep-mcp",
      "env": {
        "GOOGLE_EMAIL": "your@gmail.com",
        "GOOGLE_MASTER_TOKEN": "aas_et/..."
      }
    }
  }
}
```

On macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%\Claude\claude_desktop_config.json`

## Testing with MCP Inspector

```bash
mcp dev src/google_keep_mcp/server.py
```

## Available Tools

| Tool | Description |
|------|-------------|
| `list_notes` | List notes with optional filters (archived, pinned, color, label) |
| `get_note` | Get a note by ID |
| `create_note` | Create a text note |
| `update_note` | Update note title, text, color, pinned, or archived state |
| `delete_note` | Move a note to trash |
| `archive_note` | Archive or unarchive a note |
| `pin_note` | Pin or unpin a note |
| `create_list` | Create a checklist with optional items |
| `update_list_items` | Add, update, check, or uncheck items in a list |
| `search_notes` | Full-text search across title and body |
| `list_labels` | List all labels |
| `create_label` | Create a new label |
| `add_label_to_note` | Apply a label to a note |

## Development

```bash
# Install with dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest tests/ -v
```

## Notes

- `delete_note` moves notes to trash (Google Keep does not expose hard deletion via API)
- All mutations call `keep.sync()` automatically to persist changes to Google's servers
- The server performs a full sync on startup; subsequent mutations use incremental sync
