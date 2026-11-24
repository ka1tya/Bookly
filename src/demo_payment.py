from src.db import get_session
from src.repositories.payment_queries import monthly_payments_report, order_items_with_titles, payments_by_status_and_method


def main():
    with get_session() as session:
        print("Платежі готівкою, що очікують оплати:")
        for payment in payments_by_status_and_method(session, "очікує", "готівка"):
            print(f"  платіж {payment.id}, замовлення {payment.order_id}, {payment.amount} грн, {payment.date}")

        print("\nПозиції замовлення 5:")
        for row in order_items_with_titles(session, 5):
            print(f"  {row.title}: {row.quantity} x {row.unit_price} = {row.line_total} грн")

        print("\nПлатежі за місяцями і способами оплати:")
        for row in monthly_payments_report(session):
            print(f"  {row.month:%Y-%m} {row.method}: {row.payments_count} шт, {row.total_amount} грн, "
                  f"накопичено {row.cumulative_amount} грн, місце {row.place}")


if __name__ == "__main__":
    main()
