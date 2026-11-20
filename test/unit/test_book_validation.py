from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from src.services.book_service import (
    change_book_price,
    check_new_price,
    create_book_with_categories,
    to_decimal,
    validate_book,
)
from src.services.errors import ValidationError

YEAR = date.today().year


def test_valid_book():
    assert validate_book("Кобзар", 1840, "180.50", [4]) == Decimal("180.50")


def test_free_book():
    assert validate_book("Безкоштовна", 2020, 0, [1]) == Decimal("0")


@pytest.mark.parametrize("title, year, price, categories", [
    ("", 2020, 100, [1]),
    ("   ", 2020, 100, [1]),
    (None, 2020, 100, [1]),
    ("К" * 201, 2020, 100, [1]),
    ("Книга", 0, 100, [1]),
    ("Книга", -5, 100, [1]),
    ("Книга", YEAR + 1, 100, [1]),
    ("Книга", None, 100, [1]),
    ("Книга", "2020", 100, [1]),
    ("Книга", 2020, -1, [1]),
    ("Книга", 2020, "abc", [1]),
    ("Книга", 2020, 100, []),
    ("Книга", 2020, 100, None),
    ("Книга", 2020, 100, [1, 2, 1]),
])
def test_invalid_book(title, year, price, categories):
    with pytest.raises(ValidationError):
        validate_book(title, year, price, categories)


@pytest.mark.parametrize("value", ["abc", "", None, "NaN", "Infinity"])
def test_invalid_price(value):
    with pytest.raises(ValidationError):
        to_decimal(value)


@pytest.mark.parametrize("old, new", [
    ("100.00", "150.00"),
    ("100.00", "50.00"),
    ("100.00", "120.00"),
])
def test_allowed_price_change(old, new):
    assert check_new_price(Decimal(old), new) == Decimal(new)


@pytest.mark.parametrize("old, new", [
    ("100.00", "100.00"),
    ("100.00", "0"),
    ("100.00", "-10"),
    ("100.00", "150.01"),
    ("100.00", "49.99"),
    ("100.00", "abc"),
])
def test_forbidden_price_change(old, new):
    with pytest.raises(ValidationError):
        check_new_price(Decimal(old), new)


def test_invalid_book_not_saved():
    session = MagicMock()
    with pytest.raises(ValidationError):
        create_book_with_categories(session, 1, "", 2020, 100, [1])
    session.add.assert_not_called()
    session.commit.assert_not_called()


def test_wrong_price_rollback():
    session = MagicMock()
    session.get.return_value = MagicMock(price=Decimal("100.00"))
    with pytest.raises(ValidationError):
        change_book_price(session, 1, "500.00")
    session.commit.assert_not_called()
    session.rollback.assert_called_once()
