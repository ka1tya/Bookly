from sqlalchemy.exc import IntegrityError
from src.models import OrderItem, Payment
from src.models.constants import ORDER_NEW, ORDER_RECEIVED, PAYMENT_CASH, PAYMENT_METHODS, PAYMENT_PAID, PAYMENT_PENDING
from src.repositories import payment_repository as repo
from src.services.errors import ConflictError, NotFoundError, OrderStatusError, ValidationError

MIN_QUANTITY = 1
MAX_QUANTITY = 10

def validate_items(items, method):
    if method not in PAYMENT_METHODS:
        raise ValidationError(f"Невідомий спосіб оплати: {method}")
    if not items:
        raise ValidationError("Потрібна хоча б одна позиція")
    for item in items:
        quantity = item.get("quantity")
        if not isinstance(quantity, int) or not MIN_QUANTITY <= quantity <= MAX_QUANTITY:
            raise ValidationError(f"Кількість має бути від {MIN_QUANTITY} до {MAX_QUANTITY}")

def add_items(session, order, items):
    for item in items:
        book = repo.get_book(session, item["book_id"])
        if book is None:
            raise NotFoundError(f"Книгу {item['book_id']} не знайдено")
        session.add(OrderItem(order_id=order.id, book_id=book.id, quantity=item["quantity"], unit_price=book.price))
    session.flush()

def create_pending_payment(session, order, method):
    total = repo.items_total(session, order.id)
    payment = repo.get_payment(session, order.id)
    if payment is None:
        payment = Payment(order_id=order.id, amount=total, method=method, status=PAYMENT_PENDING)
        session.add(payment)
    elif payment.status != PAYMENT_PENDING:
        raise ConflictError("Платіж уже оплачено, суму змінити не можна")
    else:
        payment.amount = total
        payment.method = method
    session.flush()
    return payment

def add_items_to_order(session, order_id, items, method):
    validate_items(items, method)
    try:
        order = repo.get_order_for_update(session, order_id)
        if order is None:
            raise NotFoundError("Замовлення не знайдено")
        if order.status != ORDER_NEW:
            raise OrderStatusError(f"Замовлення має статус \"{order.status}\", позиції додати вже не можна")
        add_items(session, order, items)
        create_pending_payment(session, order, method)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise ConflictError("Така книга вже є в замовленні або повторюється в списку")
    except Exception:
        session.rollback()
        raise
    session.refresh(order)
    return order

def confirm_cash_payment(session, order_id):
    try:
        order = repo.get_order_for_update(session, order_id)
        if order is None:
            raise NotFoundError("Замовлення не знайдено")
        payment = repo.get_payment_for_update(session, order_id)
        if payment is None:
            raise NotFoundError("Платіж не знайдено")
        if payment.method != PAYMENT_CASH:
            raise ConflictError("Підтвердити вручну можна лише оплату готівкою")
        if payment.status != PAYMENT_PENDING:
            raise ConflictError(f"Платіж має статус \"{payment.status}\", підтвердити його не можна")
        if order.status != ORDER_RECEIVED:
            raise OrderStatusError("Готівку можна підтвердити лише після того, як замовлення отримано")
        payment.status = PAYMENT_PAID
        session.commit()
        return payment
    except Exception:
        session.rollback()
        raise

def remove_order_item(session, order_id, book_id):
    try:
        order = repo.get_order_for_update(session, order_id)
        if order is None:
            raise NotFoundError("Замовлення не знайдено")
        if order.status != ORDER_NEW:
            raise OrderStatusError(f"Замовлення має статус \"{order.status}\", позицію видалити вже не можна")
        item = repo.get_order_item(session, order_id, book_id)
        if item is None:
            raise NotFoundError("Такої позиції в замовленні немає")
        if repo.count_order_items(session, order_id) == 1:
            raise ValidationError("Остання позиція: замовлення не може бути порожнім")
        session.delete(item)
        session.flush()
        payment = repo.get_payment_for_update(session, order_id)
        if payment is not None:
            if payment.status != PAYMENT_PENDING:
                raise ConflictError("Платіж уже оплачено, суму змінити не можна")
            payment.amount = repo.items_total(session, order_id)
        session.commit()
        return order
    except Exception:
        session.rollback()
        raise
