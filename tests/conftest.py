import pytest
from unittest.mock import MagicMock, patch
import gkeepapi
import gkeepapi.node as gnode


@pytest.fixture
def mock_keep():
    """Return a mock gkeepapi.Keep instance."""
    return MagicMock(spec=gkeepapi.Keep)


@pytest.fixture(autouse=True)
def inject_keep(mock_keep, monkeypatch):
    """Inject mock Keep client into state module."""
    import google_keep_mcp._state as state_module
    monkeypatch.setattr(state_module, "_keep", mock_keep)


@pytest.fixture
def real_note():
    """Return a real gkeepapi Note with populated fields."""
    n = gnode.Note()
    n.title = "Test Note"
    n.text = "Test content"
    return n


@pytest.fixture
def real_list():
    """Return a real gkeepapi List with items."""
    lst = gnode.List()
    lst.title = "Shopping List"
    lst.add("Milk", False)
    lst.add("Eggs", True)
    return lst
