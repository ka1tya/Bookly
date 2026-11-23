import pytest

from src.repositories.payment_queries import MAX_PAGE_SIZE, page_offset
from src.services.errors import ValidationError


@pytest.mark.parametrize("page, page_size, offset", [
    (1, 10, 0),
    (2, 10, 10),
    (3, 5, 10),
    (1, 1, 0),
    (1, MAX_PAGE_SIZE, 0),
])
def test_page_offset(page, page_size, offset):
    assert page_offset(page, page_size) == offset


@pytest.mark.parametrize("page, page_size", [
    (0, 10),
    (-1, 10),
    (1, 0),
    (1, -5),
    (1, MAX_PAGE_SIZE + 1),
    ("1", 10),
    (1, "10"),
    (1.5, 10),
    (None, 10),
])
def test_wrong_page(page, page_size):
    with pytest.raises(ValidationError):
        page_offset(page, page_size)
