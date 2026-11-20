from sqlalchemy import delete
from src.models import OrderItem, Orders, Payment
from src.models.constants import ALLOWED_TRANSITIONS, ORDER_CANCELLED, ORDER_STATUSES
from src.services.errors import NotFoundError, OrderStatusError, ValidationError

def validate_status(status):
    if status not in ORDER_STATUSES:
        raise ValidationError(f"Невідомий статус замовлення \"{status}\"")

def check_transition(current_status, new_status):
    validate_status(new_status)
    if new_status not in ALLOWED_TRANSITIONS[current_status]:
        raise OrderStatusError(f"Статус \"{current_status}\" не можна змінити на \"{new_status}\"")

def lock_order(session, order_id, nowait=False):
    order = session.get(Orders, order_id, with_for_update={"nowait": nowait}, populate_existing=True)
    if order is None:
        raise NotFoundError("Замовлення не знайдено")
    return order

def change_order_status(session, order_id, new_status, nowait=False):
    validate_status(new_status)
    try:
        order = lock_order(session, order_id, nowait)
        check_transition(order.status, new_status)
        order.status = new_status
        session.commit()
        return order
    except Exception:
        session.rollback()
        raise

def delete_cancelled_order(session, order_id):
    try:
        order = lock_order(session, order_id)
        if order.status != ORDER_CANCELLED:
            raise OrderStatusError(f"Видалити можна лише скасоване замовлення, а це має статус \"{order.status}\"")
        session.execute(delete(Payment).where(Payment.order_id == order_id))
        session.execute(delete(OrderItem).where(OrderItem.order_id == order_id))
        session.delete(order)
        session.commit()
    except Exception:
        session.rollback()
        raise
