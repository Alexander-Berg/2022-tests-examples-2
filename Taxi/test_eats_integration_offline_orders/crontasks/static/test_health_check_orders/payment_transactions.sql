INSERT INTO payment_transactions (uuid, order_id, order_items, receipt_email_id, receipt_phone_id, place_id)
VALUES (
    'transaction_uuid__1',
    1,
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 1, "in_pay_count": 0, "paid_count": 0, "vat": 20.0},
    {"id": "product_id__2", "title": "Палтус за палтус", "price": 0.23, "base_price": 0.23, "quantity": 1, "in_pay_count": 0, "paid_count": 0, "vat": 20.0}]',
    'personal_email__1',
    'personal_phone__1',
    'place_id__2'
),
(
    'transaction_uuid__2',
    2,
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 1, "in_pay_count": 0, "paid_count": 0, "vat": 20.0},
    {"id": "product_id__2", "title": "Палтус за палтус", "price": 0.23, "base_price": 0.23, "quantity": 1, "in_pay_count": 0, "paid_count": 0, "vat": 20.0}]',
    'personal_email__1',
    'personal_phone__1',
    'place_id__1'
);
