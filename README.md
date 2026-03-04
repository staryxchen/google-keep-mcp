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

Google has restricted direct password-based authentication, so obtaining a master token requires a browser-based flow. The most reliable method is:

1. Open `https://accounts.google.com/EmbeddedSetup` in your browser and log in fully (including 2-step verification if enabled)
2. After login, open DevTools → **Application** (Chrome) or **Storage** (Firefox) → Cookies → `accounts.google.com`
3. Find the cookie named **`oauth_token`** (value starts with `oauth2_4/` or `oauth2_1/`) and copy it
4. Run the following to exchange it for a master token:

```bash
python3 -c "
import gpsoauth, getpass
email = input('Google email: ')
oauth_token = getpass.getpass('oauth_token cookie value: ')
result = gpsoauth.exchange_token(email, oauth_token, '0123456789abcdef')
print(result.get('Token', result))
"
```

The resulting `aas_et/...` string is your `GOOGLE_MASTER_TOKEN`.

> For more context and alternative approaches, see [kiwiz/gkeepapi#171](https://github.com/kiwiz/gkeepapi/issues/171).

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
