INSERT INTO orders (uuid, table_id, service_fee, items, items_hash, created_at,
                    updated_at, status)
VALUES
-- last_transactions
(
    'order_uuid__1',
    1,
    9.00,
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1,
    "base_price": 0.1, "quantity": 2, "in_pay_count": 0, "paid_count": 1,
    "vat": 20.0}]',
    ' - 1 ',
    '2022-05-04T09:00:00+00:00',
    '2022-05-04T09:00:00+00:00',
    'created'
),
(
    'order_uuid__2',
    1,
    9.00,
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1,
    "base_price": 0.1, "quantity": 2, "in_pay_count": 0, "paid_count": 1,
    "vat": 20.0}]',
    ' - 1 ',
    '2022-05-04T09:00:00+00:00',
    '2022-05-04T09:00:00+00:00',
    'created'
),
-- successful_orders
(
    'order_uuid__3',
    1,
    9.00,
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1,
    "base_price": 0.1, "quantity": 2, "in_pay_count": 0, "paid_count": 1,
    "vat": 20.0}]',
    ' - 1 ',
    '2022-05-04T07:29:30+00:00',
    '2022-05-04T08:29:30+00:00',
    'closed'
),
(
    'order_uuid__4',
    1,
    9.00,
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1,
    "base_price": 0.1, "quantity": 2, "in_pay_count": 0, "paid_count": 1,
    "vat": 20.0}]',
    ' - 1 ',
    '2022-05-04T07:29:30+00:00',
    '2022-05-04T08:29:30+00:00',
    'closed'
),
-- excluded from successful_orders by status and time
(
    'order_uuid__5',
    1,
    9.00,
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1,
    "base_price": 0.1, "quantity": 2, "in_pay_count": 0, "paid_count": 1,
    "vat": 20.0}]',
    ' - 1 ',
    '2022-05-04T07:29:30+00:00',
    '2022-05-04T08:29:30+00:00',
    'paid'
),
(
    'order_uuid__6',
    1,
    9.00,
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1,
    "base_price": 0.1, "quantity": 2, "in_pay_count": 0, "paid_count": 1,
    "vat": 20.0}]',
    ' - 1 ',
    '2022-05-04T07:30:30+00:00',
    '2022-05-04T08:30:30+00:00',
    'closed'
),
(
    'order_uuid__7',
    1,
    9.00,
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1,
    "base_price": 0.1, "quantity": 2, "in_pay_count": 0, "paid_count": 1,
    "vat": 20.0}]',
    ' - 1 ',
    '2022-05-04T07:28:30+00:00',
    '2022-05-04T08:28:30+00:00',
    'closed'
),
-- failed_orders
(
    'order_uuid__8',
    1,
    9.00,
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1,
    "base_price": 0.1, "quantity": 2, "in_pay_count": 0, "paid_count": 1,
    "vat": 20.0}]',
    ' - 1 ',
    '2022-05-04T08:25:30+00:00',
    '2022-05-04T08:25:30+00:00',
    'created'
),
(
    'order_uuid__9',
    1,
    9.00,
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1,
    "base_price": 0.1, "quantity": 2, "in_pay_count": 0, "paid_count": 1,
    "vat": 20.0}]',
    ' - 1 ',
    '2022-05-04T08:25:30+00:00',
    '2022-05-04T08:25:30+00:00',
    'created'
),
-- excluded from failed_orders by transactions time
(
    'order_uuid__10',
    1,
    9.00,
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1,
    "base_price": 0.1, "quantity": 2, "in_pay_count": 0, "paid_count": 1,
    "vat": 20.0}]',
    ' - 1 ',
    '2022-05-04T08:25:30+00:00',
    '2022-05-04T08:25:30+00:00',
    'created'
),
(
    'order_uuid__11',
    1,
    9.00,
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1,
    "base_price": 0.1, "quantity": 2, "in_pay_count": 0, "paid_count": 1,
    "vat": 20.0}]',
    ' - 1 ',
    '2022-05-04T08:25:30+00:00',
    '2022-05-04T08:25:30+00:00',
    'created'
),
(
    'order_uuid__12',
    1,
    9.00,
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1,
    "base_price": 0.1, "quantity": 2, "in_pay_count": 0, "paid_count": 1,
    "vat": 20.0}]',
    ' - 1 ',
    '2022-05-04T08:25:30+00:00',
    '2022-05-04T08:25:30+00:00',
    'created'
)
;
