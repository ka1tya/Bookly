import re
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from src.models import Address, Customer, Orders
from src.models.constants import ACTIVE_STATUSES
from src.services.errors import ConflictError, NotFoundError, OrderStatusError, ValidationError

EMAIL_PATTERN = r"[\w.+-]+@[\w-]+(\.[\w-]+)+"

def validate_customer(first_name, last_name, email, phone):
    if not first_name or not last_name:
        raise ValidationError("Ім'я та прізвище обов'язкові")
    if not re.fullmatch(EMAIL_PATTERN, email):
        raise ValidationError("Некоректний email")
    digits = phone.removeprefix("+")
    if not digits.isdigit() or not 10 <= len(digits) <= 15:
        raise ValidationError("Некоректний телефон")

def validate_address(address):
    for field in ["country", "city", "street"]:
        if not address.get(field):
            raise ValidationError(f"У адресі не заповнено поле {field}")

def register_customer(session, first_name, last_name, email, phone, addresses):
    validate_customer(first_name, last_name, email, phone)
    if not addresses:
        raise ValidationError("Потрібна хоча б одна адреса доставки")
    for address in addresses:
        validate_address(address)

    same_email = select(Customer).where(func.lower(Customer.email) == email.lower())
    if session.scalar(same_email):
        raise ConflictError("Клієнт з таким email уже існує")

    customer = Customer(first_name=first_name, last_name=last_name, email=email, phone=phone)
    for address in addresses:
        customer.addresses.append(Address(
            country=address["country"],
            city=address["city"],
            street=address["street"],
            postal_code=address.get("postal_code"),
        ))

    try:
        session.add(customer)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise ConflictError("Клієнт з таким email або телефоном уже існує")
    except Exception:
        session.rollback()
        raise
    return customer

def check_address_owner(session, address_id, customer_id):
    address = session.get(Address, address_id)
    if address is None:
        raise NotFoundError("Адресу не знайдено")
    if address.customer_id != customer_id:
        raise ConflictError("Адреса належить іншому клієнту")
    return address

def change_order_address(session, order_id, address_id):
    try:
        order = session.get(Orders, order_id, with_for_update=True)
        if order is None:
            raise NotFoundError("Замовлення не знайдено")
        if order.status not in ACTIVE_STATUSES:
            raise OrderStatusError(f"Замовлення має статус \"{order.status}\", адресу змінити вже не можна")
        check_address_owner(session, address_id, order.customer_id)
        order.address_id = address_id
        session.commit()
        return order
    except Exception:
        session.rollback()
        raise

def delete_customer(session, customer_id):
    customer = session.get(Customer, customer_id)
    if customer is None:
        raise NotFoundError("Клієнта не знайдено")
    try:
        session.delete(customer)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise ConflictError("Клієнта, який має замовлення, видалити не можна")
