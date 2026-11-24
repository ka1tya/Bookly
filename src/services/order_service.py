from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError
from src.models import Customer, OrderItem, Orders, Payment
from src.models.constants import ALLOWED_TRANSITIONS, ORDER_CANCELLED, ORDER_STATUSES
from src.services.book_service import get_current_prices
from src.services.customer_service import check_address_owner
from src.services.errors import ConflictError, NotFoundError, OrderStatusError, ValidationError
from src.services.payment_service import add_items, create_pending_payment, validate_items

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

def validate_order_items(items):
    book_ids = []
    for item in items:
        book_id = item.get("book_id")
        if not isinstance(book_id, int):
            raise ValidationError("У кожної позиції має бути book_id")
        book_ids.append(book_id)
    if len(set(book_ids)) != len(book_ids):
        raise ValidationError("Одна й та сама книга повторюється в списку")
    return book_ids

def create_order(session, customer_id, address_id, items, payment_method):
    validate_items(items, payment_method)
    book_ids = validate_order_items(items)
    try:
        if session.get(Customer, customer_id) is None:
            raise NotFoundError("Клієнта не знайдено")
        check_address_owner(session, address_id, customer_id)
        get_current_prices(session, book_ids)

        order = Orders(customer_id=customer_id, address_id=address_id)
        session.add(order)
        session.flush()

        add_items(session, order, items)
        create_pending_payment(session, order, payment_method)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise ConflictError("Не вдалося створити замовлення: дані змінилися, спробуйте ще раз")
    except Exception:
        session.rollback()
        raise
    session.refresh(order, ["items", "payment"])
    return order
