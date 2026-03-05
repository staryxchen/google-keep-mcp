# Google Keep MCP Server

An MCP (Model Context Protocol) server that wraps [gkeepapi](https://github.com/kiwiz/gkeepapi) to give AI assistants structured access to Google Keep notes, lists, and labels.

## Using with Claude Code

With this MCP server and the included Claude Code slash commands, you get a lightweight task management workflow directly in your coding sessions.

### Slash Commands

Copy `.claude/commands/` to `~/.claude/commands/` to make these available globally, and add the label conventions from `~/.claude/CLAUDE.md` (see below).

| Command | Usage | Description |
|---------|-------|-------------|
| `/next` | `/next` | List all `state_todo` notes grouped by project |
| `/todo` | `/todo <task description>` | Create a new task note with `state_todo` label |
| `/doing` | `/doing <note_id>` | Transition a task to `state_doing` |
| `/done` | `/done <note_id>` | Archive a task as completed |
| `/block` | `/block <note_id> <reason>` | Mark a task as self-blocked, append reason to note body |
| `/waiting` | `/waiting <note_id> <who/why>` | Mark a task as waiting on someone else, append context to note body |
| `/capture` | `/capture <content>` | Save a thought or decision to Keep |
| `/standup` | `/standup` | Generate a standup summary from current tasks |
| `/catchup` | `/catchup <project>` | Summarize all notes for a project by status |

### Label Conventions

The commands rely on a label schema defined in `~/.claude/CLAUDE.md`:

- **`state_*`** — task state, mutually exclusive: `state_todo`, `state_doing`, `state_blocking`, `state_waiting`
- **`project_*`** — project the note belongs to (one note can have multiple)
- **`time_YYYY_MM`** — month the note was created, applied automatically

### Typical Session

```
/next                                    # see what's pending
/doing 1a2b3c4d5e6f                      # start a task
/block 1a2b3c4d5e6f can't proceed, env broken  # self-blocked
/waiting 1a2b3c4d5e6f renchu reviewing the PR  # handed off
/capture decided to use SSE over polling # save a decision
/done 1a2b3c4d5e6f                       # complete a task
/standup                                 # wrap up the day
```

## Features

- **17 MCP tools** covering notes, checklists, labels, search, and note properties
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

## Claude Code Integration

Add to your MCP settings (`.claude/settings.json` or `~/.claude/settings.json`):

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

Then copy the slash commands and global CLAUDE.md as described in [Using with Claude Code](#using-with-claude-code).

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
| `untrash_note` | Restore a note from trash |
| `archive_note` | Archive or unarchive a note |
| `pin_note` | Pin or unpin a note |
| `search_notes` | Full-text search across title and body |
| `create_list` | Create a checklist with optional items |
| `update_list_items` | Add, update, check, or uncheck items in a list |
| `sort_list_items` | Sort checklist items alphabetically |
| `list_labels` | List all labels |
| `create_label` | Create a new label |
| `add_label_to_note` | Apply a label to a note |
| `remove_label_from_note` | Remove a label from a note |
| `delete_label` | Permanently delete a label from the account |

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
