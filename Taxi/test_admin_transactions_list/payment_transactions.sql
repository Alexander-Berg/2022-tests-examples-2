INSERT INTO payment_transactions (uuid, order_id, front_uuid, order_items, status, payment_type, created_at)
VALUES
(
    'transaction_uuid__1',
    1,
    'front_uuid__1',
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 2, "in_pay_count": 1, "paid_count": 0, "vat": 20.0},
    {"id": "product_id__2", "title": "Палтус за палтус", "price": 0.23, "base_price": 0.23, "quantity": 1, "in_pay_count": 1, "paid_count": 0, "vat": 20.0}]',
    'canceled',
    'payture',
    '2022-05-16T10:00:00+00:00'
),
(
    'transaction_uuid__2',
    2,
    'front_uuid__2',
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 2, "in_pay_count": 1, "paid_count": 0, "vat": 20.0},
    {"id": "product_id__2", "title": "Палтус за палтус", "price": 0.23, "base_price": 0.23, "quantity": 1, "in_pay_count": 1, "paid_count": 0, "vat": 20.0}]',
    'in_progress',
    'sbp',
    '2022-05-16T09:00:00+00:00'
),
(
    'transaction_uuid__3',
    3,
    'front_uuid__3',
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 2, "in_pay_count": 1, "paid_count": 0, "vat": 20.0},
    {"id": "product_id__2", "title": "Палтус за палтус", "price": 0.23, "base_price": 0.23, "quantity": 1, "in_pay_count": 1, "paid_count": 0, "vat": 20.0}]',
    'success',
    'payture',
    '2022-05-15T12:30:00+03:00'
),
(
    'transaction_uuid__4',
    4,
    'front_uuid__4',
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 2, "in_pay_count": 1, "paid_count": 0, "vat": 20.0},
    {"id": "product_id__2", "title": "Палтус за палтус", "price": 0.23, "base_price": 0.23, "quantity": 1, "in_pay_count": 1, "paid_count": 0, "vat": 20.0}]',
    'in_progress',
    'sbp',
    '2022-05-15T13:00:00+03:00'
),
(
    'transaction_uuid__5',
    5,
    'front_uuid__5',
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 2, "in_pay_count": 1, "paid_count": 0, "vat": 20.0},
    {"id": "product_id__2", "title": "Палтус за палтус", "price": 0.23, "base_price": 0.23, "quantity": 1, "in_pay_count": 1, "paid_count": 0, "vat": 20.0}]',
    'success',
    'badge',
    '2022-05-15T12:00:00+03:00'
)
;
