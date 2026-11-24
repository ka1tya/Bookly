import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import DataError, OperationalError
from sqlalchemy.orm import Session
from src.models import Address, Customer, Orders
from src.services.customer_service import change_order_address, delete_customer, register_customer
from src.services.errors import ConflictError, NotFoundError, OrderStatusError

pytestmark = pytest.mark.integration

LVIV = {"country": "Україна", "city": "Львів", "street": "вул. Городоцька 5", "postal_code": "79000"}
KYIV = {"country": "Україна", "city": "Київ", "street": "вул. Хрещатик 1"}

def count_customers(session):
    return session.scalar(select(func.count()).select_from(Customer))

def test_register(session):
    customer = register_customer(session, "Аврора", "Шевчук", "Avrora@gmail.com", "+380991112233", [LVIV, KYIV])

    assert customer.id is not None
    assert customer.email == "Avrora@gmail.com"
    assert len(customer.addresses) == 2

def test_register_duplicate_email(session):
    with pytest.raises(ConflictError):
        register_customer(session, "Анна", "Коваленко", "Diva@gmail.com", "+380972121211", [LVIV])
    assert count_customers(session) == 5

def test_register_duplicate_phone(session):
    with pytest.raises(ConflictError):
        register_customer(session, "Анна", "Коваленко", "swag@gmail.com", "+380501112233", [LVIV])
    assert count_customers(session) == 5

def test_register_rollback(session):
    too_long_street = {"country": "Україна", "city": "Київ", "street": "в" * 300}
    with pytest.raises(DataError):
        register_customer(session, "Анна", "Коваленко", "swag@gmail.com", "+380972121211", [LVIV, too_long_street])
    assert count_customers(session) == 5

def test_change_order_address(session, make_address):
    customer = session.get(Customer, 3)
    new_address = make_address(customer=customer, city="Одеса", street="вул. Рибальська 7")

    order = change_order_address(session, order_id=4, address_id=new_address.id)

    assert order.address_id == new_address.id

def test_change_address_shipped_order(session):
    with pytest.raises(OrderStatusError):
        change_order_address(session, order_id=2, address_id=1)

def test_change_to_other_customer_address(session):
    with pytest.raises(ConflictError):
        change_order_address(session, order_id=4, address_id=1)
    assert session.get(Orders, 4).address_id == 4

def test_change_address_missing_order(session):
    with pytest.raises(NotFoundError):
        change_order_address(session, order_id=999, address_id=1)

def test_change_to_missing_address(session):
    with pytest.raises(NotFoundError):
        change_order_address(session, order_id=4, address_id=999)
    assert session.get(Orders, 4).address_id == 4

def test_change_address_reads_fresh_status(session):
    order = session.get(Orders, 4)
    session.execute(text("UPDATE orders SET status = 'відправлено' WHERE id = 4"))

    with pytest.raises(OrderStatusError):
        change_order_address(session, order_id=order.id, address_id=4)

def test_change_address_lock(engine):
    with engine.connect() as other:
        other.begin()
        other.execute(text("SELECT id FROM orders WHERE id = 4 FOR UPDATE"))

        with Session(engine) as session:
            session.execute(text("SET lock_timeout = '1s'"))
            with pytest.raises(OperationalError):
                change_order_address(session, order_id=4, address_id=4)

        other.rollback()

def test_delete_customer(session, make_customer, make_address):
    customer = make_customer()
    make_address(customer=customer)
    make_address(customer=customer)

    delete_customer(session, customer_id=customer.id)

    assert session.get(Customer, customer.id) is None
    assert session.scalars(select(Address).where(Address.customer_id == customer.id)).all() == []

def test_delete_customer_with_orders(session):
    with pytest.raises(ConflictError):
        delete_customer(session, customer_id=1)
    assert session.get(Customer, 1) is not None

def test_delete_missing_customer(session):
    with pytest.raises(NotFoundError):
        delete_customer(session, customer_id=999)
