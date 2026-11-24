import pytest
from unittest.mock import MagicMock
from src.repositories.order_repository import customer_orders, page_offset, search_authors
from src.services.errors import ValidationError

@pytest.mark.parametrize("page, page_size, offset", [
    (1, 10, 0),
    (2, 10, 10),
    (3, 5, 10),
    (1, 100, 0),
])
def test_page_offset(page, page_size, offset):
    assert page_offset(page, page_size) == offset

@pytest.mark.parametrize("page, page_size", [
    (0, 10),
    (-1, 10),
    (1, 0),
    (1, 101),
    ("1", 10),
    (1.5, 10),
])
def test_invalid_page(page, page_size):
    with pytest.raises(ValidationError):
        page_offset(page, page_size)

@pytest.mark.parametrize("name", ["", "   ", None])
def test_search_without_name(name):
    session = MagicMock()
    with pytest.raises(ValidationError):
        search_authors(session, name)
    session.scalars.assert_not_called()

def test_orders_with_unknown_status():
    session = MagicMock()
    with pytest.raises(ValidationError):
        customer_orders(session, customer_id=1, status="втрачено")
    session.execute.assert_not_called()
