from src.db import get_session
from src.repositories.customer_repository import addresses_in_city, find_by_email, sales_by_city

def main():
    with get_session() as session:
        customer = find_by_email(session, "diva@gmail.com")
        print(f"Клієнт за email diva@gmail.com: {customer.first_name} {customer.last_name}\n")

        print("Адреси доставки в Києві:")
        for row in addresses_in_city(session, "Київ"):
            print(f"  {row.street}, {row.first_name} {row.last_name}, {row.phone}")

        print("\nПродажі за містами:")
        for row in sales_by_city(session):
            print(f"  {row.city}: клієнтів {row.customers}, замовлень {row.orders}, "
                  f"виручка {row.revenue}, середній чек {row.average_order}, частка {row.revenue_share}%")

if __name__ == "__main__":
    main()
