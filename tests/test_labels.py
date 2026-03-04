from unittest.mock import MagicMock


def test_list_labels_empty(mock_keep):
    mock_keep.labels.return_value = iter([])
    from google_keep_mcp._state import get_keep
    keep = get_keep()
    labels = list(keep.labels())
    assert labels == []


def test_list_labels_returns_all(mock_keep):
    label1 = MagicMock()
    label1.id = "lbl1"
    label1.name = "Work"
    label2 = MagicMock()
    label2.id = "lbl2"
    label2.name = "Personal"
    mock_keep.labels.return_value = iter([label1, label2])

    from google_keep_mcp._state import get_keep
    keep = get_keep()
    labels = list(keep.labels())
    assert len(labels) == 2
    names = {lbl.name for lbl in labels}
    assert "Work" in names
    assert "Personal" in names


def test_create_label_success(mock_keep):
    mock_keep.findLabel.return_value = None
    new_label = MagicMock()
    new_label.id = "lbl_new"
    new_label.name = "NewLabel"
    mock_keep.createLabel.return_value = new_label

    from google_keep_mcp._state import get_keep
    keep = get_keep()
    existing = keep.findLabel("NewLabel")
    assert existing is None
    lbl = keep.createLabel("NewLabel")
    keep.sync()
    assert lbl.name == "NewLabel"
    mock_keep.sync.assert_called_once()


def test_create_label_duplicate_detected(mock_keep):
    existing = MagicMock()
    existing.id = "lbl_existing"
    mock_keep.findLabel.return_value = existing

    from google_keep_mcp._state import get_keep
    keep = get_keep()
    found = keep.findLabel("Duplicate")
    assert found is not None
    assert found.id == "lbl_existing"


def test_add_label_to_note(mock_keep, real_note):
    label = MagicMock()
    label.id = "lbl1"
    label.name = "Work"
    mock_keep.get.return_value = real_note
    mock_keep.findLabel.return_value = label

    from google_keep_mcp._state import get_keep
    keep = get_keep()
    note = keep.get(real_note.id)
    lbl = keep.findLabel("Work")
    note.labels.add(lbl)
    keep.sync()
    mock_keep.sync.assert_called_once()


def test_add_label_note_not_found(mock_keep):
    mock_keep.get.return_value = None
    from google_keep_mcp._state import get_keep
    keep = get_keep()
    note = keep.get("missing_id")
    assert note is None
