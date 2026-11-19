import pytest
from src.models import Orders
from src.models.constants import ORDER_CANCELLED
from src.repositories.customer_repository import addresses_in_city, find_by_email, sales_by_city

pytestmark = pytest.mark.integration

def test_find_by_email(session):
    customer = find_by_email(session, "diva@gmail.com")
    assert customer.first_name == "Олена"
    assert customer.last_name == "Іваненко"

def test_find_by_email_any_case(session):
    customer = find_by_email(session, "Diva@Gmail.com")
    assert customer.first_name == "Олена"

def test_find_missing_customer(session):
    assert find_by_email(session, "nobody@gmail.com") is None

def test_addresses_in_city(session):
    rows = addresses_in_city(session, "Київ")
    assert [row.street for row in rows] == ["вул. Борщагівська 14", "просп. Берестейський 25"]
    assert rows[0].last_name == "Іваненко"

def test_addresses_in_city_second_page(session):
    rows = addresses_in_city(session, "Київ", limit=1, offset=1)
    assert [row.street for row in rows] == ["просп. Берестейський 25"]

def test_sales_by_city(session):
    rows = sales_by_city(session)
    assert [(row.city, row.customers, row.orders, row.revenue) for row in rows] == [
        ("Київ", 1, 2, 950),
        ("Одеса", 1, 1, 260),
        ("Нью-Йорк", 1, 1, 200),
    ]
    assert rows[0].average_order == 475

def test_sales_revenue_share(session):
    shares = [row.revenue_share for row in sales_by_city(session)]
    assert [float(share) for share in shares] == [67.4, 18.4, 14.2]

def test_sales_without_cancelled(session):
    session.get(Orders, 4).status = ORDER_CANCELLED
    session.flush()
    cities = [row.city for row in sales_by_city(session)]
    assert "Одеса" not in cities
    assert "Харків" not in cities
