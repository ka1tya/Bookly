import pytest
from src.services.errors import ValidationError
from src.services.payment_service import validate_items

def test_valid_items():
    validate_items([{"book_id": 1, "quantity": 1}, {"book_id": 2, "quantity": 10}], "картка")

@pytest.mark.parametrize("quantity", [0, 11, -1, None, "2", 1.5])
def test_invalid_quantity(quantity):
    with pytest.raises(ValidationError):
        validate_items([{"book_id": 1, "quantity": quantity}], "картка")

def test_missing_quantity():
    with pytest.raises(ValidationError):
        validate_items([{"book_id": 1}], "картка")

def test_empty_items():
    with pytest.raises(ValidationError):
        validate_items([], "картка")

@pytest.mark.parametrize("method", ["біткоїн", "", None])
def test_invalid_method(method):
    with pytest.raises(ValidationError):
        validate_items([{"book_id": 1, "quantity": 1}], method)
