from sqlalchemy import func, select
from src.models import Address, Customer, OrderItem, Orders
from src.models.constants import ORDER_CANCELLED

def find_by_email(session, email):
    query = select(Customer).where(func.lower(Customer.email) == email.lower())
    return session.scalar(query)

def addresses_in_city(session, city, limit=10, offset=0):
    query = (
        select(Customer.first_name, Customer.last_name, Customer.phone, Address.street, Address.postal_code)
        .join(Address, Address.customer_id == Customer.id)
        .where(Address.city == city)
        .order_by(Address.street, Address.id)
        .limit(limit)
        .offset(offset)
    )
    return session.execute(query).all()

def sales_by_city(session):
    city_sales = (
        select(
            Address.city,
            func.count(func.distinct(Orders.customer_id)).label("customers"),
            func.count(func.distinct(Orders.id)).label("orders"),
            func.sum(OrderItem.quantity * OrderItem.unit_price).label("revenue"),
        )
        .join(Orders, Orders.address_id == Address.id)
        .join(OrderItem, OrderItem.order_id == Orders.id)
        .where(Orders.status != ORDER_CANCELLED)
        .group_by(Address.city)
        .cte("city_sales")
    )
    total_revenue = select(func.sum(city_sales.c.revenue)).scalar_subquery()
    query = (
        select(
            city_sales.c.city,
            city_sales.c.customers,
            city_sales.c.orders,
            city_sales.c.revenue,
            func.round(city_sales.c.revenue / city_sales.c.orders, 2).label("average_order"),
            func.round(100 * city_sales.c.revenue / total_revenue, 1).label("revenue_share"),
        )
        .order_by(city_sales.c.revenue.desc())
    )
    return session.execute(query).all()
