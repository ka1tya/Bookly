from src.db import get_session
from src.repositories.order_repository import customer_orders, orders_audit, search_authors

def main():
    with get_session() as session:
        print("Автори, у яких в імені або прізвищі є \"ко\":")
        for author in search_authors(session, "ко"):
            print(f"  {author.id}. {author.first_name} {author.last_name}")

        print("\nЗамовлення клієнта 1:")
        for row in customer_orders(session, 1):
            print(f"  №{row.id} від {row.date}, {row.status}, {row.city}, {row.street}")

        print("\nЗамовлення клієнта 1 зі статусом \"отримано\":")
        for row in customer_orders(session, 1, status="отримано"):
            print(f"  №{row.id} від {row.date}, {row.status}, {row.city}, {row.street}")

        print("\nАудит замовлень:")
        rows = orders_audit(session)
        if not rows:
            print("  проблемних замовлень немає")
        for row in rows:
            print(f"  №{row.order_id} ({row.status}): позицій {row.items_count}, сума {row.items_total}, "
                  f"платіж {row.paid_amount}, порожнє {row.empty_order}, без платежу {row.no_payment}, "
                  f"сума не збігається {row.amount_mismatch}, готівка оплачена раніше {row.cash_paid_early}")

if __name__ == "__main__":
    main()
