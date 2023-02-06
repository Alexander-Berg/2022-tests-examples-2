 INSERT INTO orders (uuid, table_id, items, items_hash, updated_at, status)
 VALUES
(
    'order_uuid__1',
    1,
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 2, "in_pay_count": 1, "paid_count": 0, "vat": 20.0},
    {"id": "product_id__2", "title": "Палтус за палтус", "price": 0.23, "base_price": 0.23, "quantity": 1, "in_pay_count": 1, "paid_count": 0, "vat": 20.0}]',
    '-831397301969266000',
    '2022-05-15 12:28:00',
    'paid'
),
(
    'order_uuid__2',
    1,
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 2, "in_pay_count": 1, "paid_count": 0, "vat": 20.0},
    {"id": "product_id__2", "title": "Палтус за палтус", "price": 0.23, "base_price": 0.23, "quantity": 1, "in_pay_count": 1, "paid_count": 0, "vat": 20.0}]',
    '-831397301969266000',
    '2022-05-15 12:29:30',
    'paid'
),
(
    'order_uuid__3',
    1,
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 2, "in_pay_count": 1, "paid_count": 0, "vat": 20.0},
    {"id": "product_id__2", "title": "Палтус за палтус", "price": 0.23, "base_price": 0.23, "quantity": 1, "in_pay_count": 1, "paid_count": 0, "vat": 20.0}]',
    '-831397301969266000',
    '2022-05-15 12:28:30',
    'closed'
),
(
    'order_uuid__4',
    2,
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 2, "in_pay_count": 1, "paid_count": 0, "vat": 20.0},
    {"id": "product_id__2", "title": "Палтус за палтус", "price": 0.23, "base_price": 0.23, "quantity": 1, "in_pay_count": 1, "paid_count": 0, "vat": 20.0}]',
    '-831397301969266000',
    '2022-05-15 12:27:30',
    'paid'
),
(
    'order_uuid__5',
    2,
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 2, "in_pay_count": 1, "paid_count": 0, "vat": 20.0},
    {"id": "product_id__2", "title": "Палтус за палтус", "price": 0.23, "base_price": 0.23, "quantity": 1, "in_pay_count": 1, "paid_count": 0, "vat": 20.0}]',
    '-831397301969266000',
    '2022-05-15 12:24:30',
    'paid'
)
        ;
