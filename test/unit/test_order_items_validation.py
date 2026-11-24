import pytest
from unittest.mock import MagicMock
from src.services.errors import ValidationError
from src.services.order_service import create_order, validate_order_items

def test_valid_items():
    assert validate_order_items([{"book_id": 1, "quantity": 1}, {"book_id": 2, "quantity": 3}]) == [1, 2]

def test_same_book_twice():
    with pytest.raises(ValidationError):
        validate_order_items([{"book_id": 1, "quantity": 1}, {"book_id": 1, "quantity": 2}])

@pytest.mark.parametrize("item", [{"quantity": 1}, {"book_id": None, "quantity": 1}, {"book_id": "1", "quantity": 1}])
def test_wrong_book_id(item):
    with pytest.raises(ValidationError):
        validate_order_items([item])

@pytest.mark.parametrize("items, method", [
    ([], "картка"),
    ([{"book_id": 1, "quantity": 11}], "картка"),
    ([{"book_id": 1, "quantity": 0}], "картка"),
    ([{"book_id": 1, "quantity": 1}], "біткоїн"),
    ([{"book_id": 1, "quantity": 1}, {"book_id": 1, "quantity": 1}], "картка"),
])
def test_invalid_order_does_not_touch_db(items, method):
    session = MagicMock()
    with pytest.raises(ValidationError):
        create_order(session, customer_id=1, address_id=1, items=items, payment_method=method)
    session.get.assert_not_called()
    session.commit.assert_not_called()
