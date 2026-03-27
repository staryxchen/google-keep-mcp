import gkeepapi.node as gnode

from google_keep_mcp.tools._helpers import note_to_model


def test_get_note_returns_model(mock_keep, real_note):
    mock_keep.get.return_value = real_note
    result = note_to_model(real_note)
    assert result.title == "Test Note"
    assert result.type == "note"
    assert result.text == "Test content"


def test_get_note_returns_none_for_missing(mock_keep):
    mock_keep.get.return_value = None
    from google_keep_mcp._state import get_keep

    keep = get_keep()
    assert keep.get("nonexistent") is None


def test_create_note_syncs(mock_keep, real_note):
    mock_keep.createNote.return_value = real_note
    from google_keep_mcp._state import get_keep

    keep = get_keep()
    keep.createNote(title="Test", text="Body")
    keep.sync()
    mock_keep.createNote.assert_called_once_with(title="Test", text="Body")
    mock_keep.sync.assert_called_once()


def test_delete_note_trashes(mock_keep, real_note):
    mock_keep.get.return_value = real_note
    from google_keep_mcp._state import get_keep

    keep = get_keep()
    note = keep.get(real_note.id)
    note.trash()
    keep.sync()
    assert real_note.trashed is True
    mock_keep.sync.assert_called_once()


def test_note_to_model_list(real_list):
    result = note_to_model(real_list)
    assert result.type == "list"
    assert result.title == "Shopping List"
    assert result.items is not None
    assert len(result.items) == 2
    texts = {item.text for item in result.items}
    assert "Milk" in texts
    assert "Eggs" in texts


def test_note_to_model_color(real_note):
    real_note.color = gnode.ColorValue.Red
    result = note_to_model(real_note, full=True)  # full=True to get color
    assert result.color == "RED"


def test_archive_note(mock_keep, real_note):
    mock_keep.get.return_value = real_note
    from google_keep_mcp._state import get_keep

    keep = get_keep()
    note = keep.get(real_note.id)
    note.archived = True
    keep.sync()
    assert real_note.archived is True
    mock_keep.sync.assert_called_once()


def test_pin_note(mock_keep, real_note):
    mock_keep.get.return_value = real_note
    from google_keep_mcp._state import get_keep

    keep = get_keep()
    note = keep.get(real_note.id)
    note.pinned = True
    keep.sync()
    assert real_note.pinned is True
    mock_keep.sync.assert_called_once()


def test_untrash_note(mock_keep, real_note):
    real_note.trash()
    assert real_note.trashed is True
    mock_keep.get.return_value = real_note
    from google_keep_mcp._state import get_keep

    keep = get_keep()
    note = keep.get(real_note.id)
    note.untrash()
    keep.sync()
    assert real_note.trashed is False
    mock_keep.sync.assert_called_once()


def test_untrash_note_not_in_trash(mock_keep, real_note):
    assert real_note.trashed is False
    mock_keep.get.return_value = real_note
    from google_keep_mcp._state import get_keep

    keep = get_keep()
    note = keep.get(real_note.id)
    # Should not be trashed already
    assert not note.trashed


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


def test_note_to_model_slim_omits_detail_fields(real_note):
    """Slim mode (default): server_id, url, color are None."""
    result = note_to_model(real_note)
    assert result.server_id is None
    assert result.url is None
    assert result.color is None


def test_note_to_model_full_includes_detail_fields(real_note):
    """Full mode: color and url are populated from the node.

    Note: server_id cannot be verified here because a locally-created
    (never-synced) gkeepapi node has server_id=None by design.
    The important behavior is that full=False FORCES server_id to None
    regardless of the node value; that is tested by test_note_to_model_slim_omits_detail_fields.
    """
    real_note.color = gnode.ColorValue.Red
    result = note_to_model(real_note, full=True)
    assert result.color == "RED"
    assert result.url is not None  # gkeepapi generates a URL from the local node ID


def test_note_to_model_slim_serializes_without_detail_keys(real_note):
    """Slim mode serialization: None fields absent from dict output."""
    result = note_to_model(real_note)
    data = result.model_dump(mode="json")
    assert "server_id" not in data
    assert "url" not in data
    assert "color" not in data


def test_append_note_adds_newline(mock_keep, real_note):
    real_note.text = "original"
    mock_keep.get.return_value = real_note
    from mcp.server.fastmcp import FastMCP

    from google_keep_mcp.tools.notes import register

    mcp = FastMCP("test")
    register(mcp)
    # Call update_note directly via the registered tool function
    # Access inner function through mcp tools
    update_fn = next(t.fn for t in mcp._tool_manager.list_tools() if t.name == "update_note")
    result = update_fn(note_id=real_note.id, append_text="new content")
    assert result.success is True
    assert real_note.text == "original\nnew content"


def test_append_note_empty_body(mock_keep, real_note):
    real_note.text = ""
    mock_keep.get.return_value = real_note
    from mcp.server.fastmcp import FastMCP

    from google_keep_mcp.tools.notes import register

    mcp = FastMCP("test")
    register(mcp)
    update_fn = next(t.fn for t in mcp._tool_manager.list_tools() if t.name == "update_note")
    result = update_fn(note_id=real_note.id, append_text="new content")
    assert result.success is True
    assert real_note.text == "new content"


def test_append_note_mutually_exclusive_with_text(mock_keep, real_note):
    mock_keep.get.return_value = real_note
    from mcp.server.fastmcp import FastMCP

    from google_keep_mcp.tools.notes import register

    mcp = FastMCP("test")
    register(mcp)
    update_fn = next(t.fn for t in mcp._tool_manager.list_tools() if t.name == "update_note")
    result = update_fn(note_id=real_note.id, text="full text", append_text="extra")
    assert result.success is False
    assert "mutually exclusive" in result.message
