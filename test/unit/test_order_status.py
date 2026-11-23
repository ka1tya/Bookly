import pytest
from unittest.mock import MagicMock
from src.models.constants import (
    ALLOWED_TRANSITIONS, ORDER_ASSEMBLING, ORDER_CANCELLED, ORDER_NEW,
    ORDER_RECEIVED, ORDER_SHIPPED, ORDER_STATUSES,
)
from src.services.errors import OrderStatusError, ValidationError
from src.services.order_service import change_order_status, check_transition

ALLOWED = [
    (ORDER_NEW, ORDER_ASSEMBLING),
    (ORDER_NEW, ORDER_CANCELLED),
    (ORDER_ASSEMBLING, ORDER_SHIPPED),
    (ORDER_ASSEMBLING, ORDER_CANCELLED),
    (ORDER_SHIPPED, ORDER_RECEIVED),
]

FORBIDDEN = [
    (current, new)
    for current in ORDER_STATUSES
    for new in ORDER_STATUSES
    if (current, new) not in ALLOWED
]

def test_every_status_has_transitions():
    assert set(ALLOWED_TRANSITIONS) == set(ORDER_STATUSES)

@pytest.mark.parametrize("current, new", ALLOWED)
def test_allowed_transition(current, new):
    check_transition(current, new)

@pytest.mark.parametrize("current, new", FORBIDDEN)
def test_forbidden_transition(current, new):
    with pytest.raises(OrderStatusError):
        check_transition(current, new)

@pytest.mark.parametrize("status", [ORDER_RECEIVED, ORDER_CANCELLED])
def test_final_status_cannot_change(status):
    assert ALLOWED_TRANSITIONS[status] == ()

@pytest.mark.parametrize("status", ["втрачено", "", "НОВЕ"])
def test_unknown_status(status):
    with pytest.raises(ValidationError):
        check_transition(ORDER_NEW, status)

def test_change_to_unknown_status_does_not_touch_db():
    session = MagicMock()
    with pytest.raises(ValidationError):
        change_order_status(session, order_id=4, new_status="втрачено")
    session.get.assert_not_called()
    session.commit.assert_not_called()
