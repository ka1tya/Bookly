from datetime import date
from decimal import Decimal, InvalidOperation

from psycopg.errors import ForeignKeyViolation, LockNotAvailable
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError

from src.models import Author, Book
from src.repositories.book_repository import add_categories, in_orders, lock_book
from src.services.book_errors import BookInOrdersError
from src.services.errors import ConflictError, LockedError, NotFoundError, ValidationError


def to_decimal(value):
    try:
        price = Decimal(str(value))
    except InvalidOperation:
        raise ValidationError("Ціна має бути числом")
    if not price.is_finite():
        raise ValidationError("Ціна має бути числом")
    return price


def validate_book(title, year, price, category_ids):
    if not isinstance(title, str) or not title.strip():
        raise ValidationError("Назва книги не може бути порожньою")
    if len(title.strip()) > 200:
        raise ValidationError("Назва книги задовга")
    if not isinstance(year, int) or year < 1 or year > date.today().year:
        raise ValidationError("Некоректний рік видання")
    price = to_decimal(price)
    if price < 0:
        raise ValidationError("Ціна не може бути від'ємною")
    if not category_ids:
        raise ValidationError("Потрібна хоча б одна категорія")
    if len(set(category_ids)) != len(category_ids):
        raise ValidationError("Категорії в списку повторюються")
    return price


def create_book_with_categories(session, author_id, title, published_year, price, category_ids):
    price = validate_book(title, published_year, price, category_ids)
    try:
        if session.get(Author, author_id) is None:
            raise NotFoundError("Автора не знайдено")

        book = Book(author_id=author_id, title=title.strip(), published_year=published_year, price=price)
        session.add(book)
        session.flush()

        try:
            add_categories(session, book.id, category_ids)
        except IntegrityError as e:
            if isinstance(e.orig, ForeignKeyViolation):
                raise NotFoundError("Категорію не знайдено")
            raise

        session.commit()
    except IntegrityError:
        session.rollback()
        raise ConflictError("Не вдалося зберегти книгу")
    except Exception:
        session.rollback()
        raise
    session.refresh(book, ["author", "categories"])
    return book


def check_new_price(old, new):
    new = to_decimal(new)
    if new <= 0:
        raise ValidationError("Ціна має бути більшою за 0")
    if new == old:
        raise ValidationError("Нова ціна така сама, як поточна")
    if abs(new - old) > old / 2:
        raise ValidationError("Ціну можна змінити не більше ніж на 50%")
    return new


def change_book_price(session, book_id, new_price, nowait=False):
    try:
        book = lock_book(session, book_id, nowait)
        if book is None:
            raise NotFoundError("Книгу не знайдено")
        book.price = check_new_price(book.price, new_price)
        session.commit()
        return book
    except OperationalError as e:
        session.rollback()
        if isinstance(e.orig, LockNotAvailable):
            raise LockedError("Книгу зараз змінює інший користувач")
        raise
    except Exception:
        session.rollback()
        raise


def delete_book_not_in_orders(session, book_id):
    try:
        book = lock_book(session, book_id)
        if book is None:
            raise NotFoundError("Книгу не знайдено")
        if in_orders(session, book_id):
            raise BookInOrdersError("Книга є в замовленнях, видалити її не можна")
        book.categories.clear()
        session.flush()
        session.delete(book)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise BookInOrdersError("Книга пов'язана з іншими записами")
    except Exception:
        session.rollback()
        raise


def get_current_prices(session, book_ids):
    ids = set(book_ids)
    if not ids:
        return {}
    rows = session.execute(select(Book.id, Book.price).where(Book.id.in_(ids))).all()
    prices = {book_id: price for book_id, price in rows}
    missing = ids - prices.keys()
    if missing:
        raise NotFoundError(f"Книги {sorted(missing)} не знайдено")
    return prices
