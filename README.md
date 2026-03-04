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

## Use Cases in Development Workflows

Google Keep is often used as a lightweight task and note system alongside coding work. With this MCP server, Claude can read and write Keep directly, enabling workflows like:

**Task management during coding sessions**
- "What's on my `state_todo` list for this project?" — Claude queries notes by label and summarizes what's pending
- "Mark the authentication task as doing" — Claude removes the `state_todo` label and adds `state_doing`
- "Add a note that the rate limiter is blocking the deploy" — Claude creates a note tagged `state_blocking` with context you dictate

**Capturing decisions and context while coding**
- "Save a note with today's architecture decision: we chose SSE over polling because..." — keeps a searchable log without leaving the editor
- "Search my notes for anything related to the OAuth flow" — Claude searches across all notes and surfaces relevant ones
- After a debugging session: "Create a note summarizing what we found and what still needs investigation"

**Daily standups and reviews**
- "Summarize everything tagged `person_daily` from this month" — Claude reads notes filtered by the `time_2026_03` label and drafts a summary
- "What did I work on last week?" — Claude searches notes by time label and lists completed items
- "Create a checklist for tomorrow's code review" — Claude creates a list note with items you specify

**Project context across tools**
- Keep notes act as a persistent scratchpad that Claude can read at the start of a session: "Catch me up on the `project_google-keep-mcp` notes"
- "Archive all notes tagged `project_harp` that are marked done" — bulk operations across a project's notes

## Notes

- `delete_note` moves notes to trash (Google Keep does not expose hard deletion via API)
- All mutations call `keep.sync()` automatically to persist changes to Google's servers
- The server performs a full sync on startup; subsequent mutations use incremental sync
