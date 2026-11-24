from decimal import Decimal

from sqlalchemy import func, select
from src.models import Book, OrderItem, Orders, Payment

def get_order_for_update(session, order_id):
    return session.get(Orders, order_id, with_for_update=True, populate_existing=True)

def get_payment_for_update(session, order_id):
    query = select(Payment).where(Payment.order_id == order_id).with_for_update()
    return session.scalar(query, execution_options={"populate_existing": True})

def get_payment(session, order_id):
    return session.scalar(select(Payment).where(Payment.order_id == order_id))

def get_book(session, book_id):
    return session.get(Book, book_id)

def get_order_item(session, order_id, book_id):
    return session.get(OrderItem, (order_id, book_id))

def count_order_items(session, order_id):
    query = select(func.count()).select_from(OrderItem).where(OrderItem.order_id == order_id)
    return session.scalar(query)

def items_total(session, order_id) -> Decimal:
    query = select(func.coalesce(func.sum(OrderItem.quantity * OrderItem.unit_price), 0)).where(OrderItem.order_id == order_id)
    return session.scalar(query)
