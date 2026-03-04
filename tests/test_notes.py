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
    result = note_to_model(real_note)
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
