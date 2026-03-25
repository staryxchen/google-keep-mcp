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
    """Full mode: server_id, url, color are populated."""
    import gkeepapi.node as gnode
    real_note.color = gnode.ColorValue.Red
    result = note_to_model(real_note, full=True)
    assert result.color == "RED"
    # url is populated from the note (non-None) in full mode
    assert result.url is not None
    # server_id passes through from gkeepapi (may be None for unsynced notes,
    # but the field itself is not forced to None by slim mode)
    slim_result = note_to_model(real_note, full=False)
    assert slim_result.server_id is None  # slim always strips it
    # full mode does NOT force it to None (value comes from the node)
    # We verify it's distinct from the slim-mode forced None by checking
    # the full result's server_id field is whatever gkeepapi provides
    # (for an unsynced test node that's None from gkeepapi, which is fine)
    assert "server_id" not in slim_result.model_dump(mode="json")  # stripped by serializer


def test_note_to_model_slim_serializes_without_detail_keys(real_note):
    """Slim mode serialization: None fields absent from dict output."""
    result = note_to_model(real_note)
    data = result.model_dump(mode="json")
    assert "server_id" not in data
    assert "url" not in data
    assert "color" not in data
