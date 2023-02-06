INSERT INTO payment_transactions (uuid, order_id, order_items)
VALUES (
    'transaction_uuid__1',
    1,
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "quantity": 1, "vat": 20.0},
    {"id": "product_id__2", "title": "Палтус за палтус", "price": 0.23, "quantity": 1, "vat": 20.0},
    {"id": "service_fee", "title": "Сервисный сбор", "price": 9.0, "quantity": 1, "vat": 20.0}]'
)
