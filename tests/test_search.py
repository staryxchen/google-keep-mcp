from google_keep_mcp.tools._helpers import note_to_model


def test_search_returns_results(mock_keep, real_note):
    mock_keep.find.return_value = [real_note]
    from google_keep_mcp._state import get_keep
    keep = get_keep()
    results = list(keep.find(query="Test"))
    assert len(results) == 1
    assert results[0].title == "Test Note"


def test_search_empty_results(mock_keep):
    mock_keep.find.return_value = []
    from google_keep_mcp._state import get_keep
    keep = get_keep()
    results = list(keep.find(query="nonexistent"))
    assert results == []


def test_search_includes_both_types(mock_keep, real_note, real_list):
    mock_keep.find.return_value = [real_note, real_list]
    from google_keep_mcp._state import get_keep
    keep = get_keep()
    results = list(keep.find(query=""))
    models = [note_to_model(r) for r in results]
    types = {m.type for m in models}
    assert "note" in types
    assert "list" in types
