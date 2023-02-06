INSERT INTO payment_transactions (uuid, order_id, order_items, receipt_email_id)
VALUES (
    'transaction_uuid__1',
    1,
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 1, "in_pay_count": 0, "paid_count": 0, "vat": 20.0},
    {"id": "product_id__2", "title": "Модификатор с ценой 0", "price": 0.0, "base_price": 0.0, "quantity": 1, "in_pay_count": 0, "paid_count": 0, "vat": 20.0}]',
    'personal_email__1'
)
