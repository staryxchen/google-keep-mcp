import gkeepapi.node as gnode
from google_keep_mcp.tools._helpers import note_to_model


def test_create_list_syncs(mock_keep, real_list):
    mock_keep.createList.return_value = real_list
    from google_keep_mcp._state import get_keep
    keep = get_keep()
    keep.createList(title="Shopping List", items=[("Milk", False), ("Eggs", True)])
    keep.sync()
    mock_keep.createList.assert_called_once()
    mock_keep.sync.assert_called_once()


def test_update_list_add_item(mock_keep, real_list):
    mock_keep.get.return_value = real_list
    from google_keep_mcp._state import get_keep
    keep = get_keep()
    lst = keep.get(real_list.id)
    lst.add("Butter", False)
    keep.sync()
    texts = {li.text for li in real_list.items}
    assert "Butter" in texts
    mock_keep.sync.assert_called_once()


def test_update_list_check_all(real_list):
    for li in real_list.items:
        li.checked = True
    assert all(li.checked for li in real_list.items)


def test_update_list_uncheck_all(real_list):
    for li in real_list.items:
        li.checked = False
    assert all(not li.checked for li in real_list.items)


def test_real_note_is_not_list_type(real_note):
    assert not isinstance(real_note, gnode.List)


def test_list_to_model(real_list):
    result = note_to_model(real_list)
    assert result.type == "list"
    assert result.items is not None
    assert len(result.items) == 2
