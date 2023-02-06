INSERT INTO payment_transactions (uuid, order_id, order_items, payment_type, front_uuid, side_payment_id, status, place_id, created_at)
VALUES (
    'transaction_uuid__1',
    1,
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1,
    "base_price": 0.1, "quantity": 1, "in_pay_count": 0, "paid_count": 0,
    "vat": 20.0},
       {"id" : "product_id__2", "title": "Палтус за палтус", "price": 0.2,
    "base_price": 0.2, "quantity": 1, "in_pay_count": 0, "paid_count": 0,
    "vat": 20.0}]',
    'badge',
    'transaction_front_uuid__1',
    1,
    'in_progress',
    'place_id__1',
    '2022-06-29 00:00:30+00:00'
),
(
    'transaction_uuid__2',
    1,
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1,
    "base_price": 0.1, "quantity": 1, "in_pay_count": 0, "paid_count": 0,
    "vat": 20.0},
       {"id" : "product_id__2", "title": "Палтус за палтус", "price": 0.2,
    "base_price": 0.2, "quantity": 1, "in_pay_count": 0, "paid_count": 0,
    "vat": 20.0}]',
    'trust_card',
    'transaction_front_uuid__2',
    1,
    'in_progress',
    'place_id__1',
    '2022-06-29 00:00:00+00:00'
)
