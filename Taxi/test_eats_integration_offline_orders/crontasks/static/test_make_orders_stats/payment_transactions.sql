INSERT INTO payment_transactions (uuid, order_id, status, order_items, created_at)
VALUES
-- last_transactions
(
    'transaction_uuid__1',
    1,
    'failed',
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 1, "in_pay_count": 0, "paid_count": 0, "vat": 20.0}]',
    '2022-05-04T09:00:00+00:00'
),
(
    'transaction_uuid__2',
    1,
    'canceled',
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 1, "in_pay_count": 0, "paid_count": 0, "vat": 20.0}]',
    '2022-05-04T08:20:00+00:00'
),
(
    'transaction_uuid__3',
    1,
    'canceled',
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 1, "in_pay_count": 0, "paid_count": 0, "vat": 20.0}]',
    '2022-05-04T09:20:00+00:00'
),
(
    'transaction_uuid__4',
    1,
    'cancelled_by_user',
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 1, "in_pay_count": 0, "paid_count": 0, "vat": 20.0}]',
    '2022-05-04T09:20:00+00:00'
),
(
    'transaction_uuid__5',
    2,
    'order_time_out',
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 1, "in_pay_count": 0, "paid_count": 0, "vat": 20.0}]',
    '2022-05-04T09:20:00+00:00'
),
(
    'transaction_uuid__6',
    2,
    'success',
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 1, "in_pay_count": 0, "paid_count": 0, "vat": 20.0}]',
    '2022-05-04T09:20:00+00:00'
),
-- successful_orders
(
    'transaction_uuid__7',
    3,
    'success',
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 1, "in_pay_count": 0, "paid_count": 0, "vat": 20.0}]',
    '2022-05-04T08:20:00+00:00'
),
(
    'transaction_uuid__8',
    3,
    'cancelled_by_user',
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 1, "in_pay_count": 0, "paid_count": 0, "vat": 20.0}]',
    '2022-05-04T08:20:00+00:00'
),
(
    'transaction_uuid__9',
    3,
    'canceled',
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 1, "in_pay_count": 0, "paid_count": 0, "vat": 20.0}]',
    '2022-05-04T08:20:00+00:00'
),
-- excluded from successful_orders by status and time
(
    'transaction_uuid__10',
    4,
    'canceled',
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 1, "in_pay_count": 0, "paid_count": 0, "vat": 20.0}]',
    '2022-05-04T08:20:00+00:00'
),
(
    'transaction_uuid__11',
    5,
    'canceled',
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 1, "in_pay_count": 0, "paid_count": 0, "vat": 20.0}]',
    '2022-05-04T08:20:00+00:00'
),
(
    'transaction_uuid__12',
    6,
    'canceled',
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 1, "in_pay_count": 0, "paid_count": 0, "vat": 20.0}]',
    '2022-05-04T08:20:00+00:00'
),
(
    'transaction_uuid__13',
    7,
    'canceled',
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 1, "in_pay_count": 0, "paid_count": 0, "vat": 20.0}]',
    '2022-05-04T08:20:00+00:00'
),
-- failed_orders
(
    'transaction_uuid__14',
    8,
    'canceled',
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 1, "in_pay_count": 0, "paid_count": 0, "vat": 20.0}]',
    '2022-05-04T08:29:30+00:00'
),
(
    'transaction_uuid__15',
    8,
    'cancelled_by_user',
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 1, "in_pay_count": 0, "paid_count": 0, "vat": 20.0}]',
    '2022-05-04T08:20:00+00:00'
),
(
    'transaction_uuid__16',
    8,
    'success',
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 1, "in_pay_count": 0, "paid_count": 0, "vat": 20.0}]',
    '2022-05-04T08:20:00+00:00'
),
(
    'transaction_uuid__17',
    9,
    'canceled',
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 1, "in_pay_count": 0, "paid_count": 0, "vat": 20.0}]',
    '2022-05-04T08:29:30+00:00'
),
-- excluded from failed_orders by transactions time
(
    'transaction_uuid__18',
    10,
    'canceled',
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 1, "in_pay_count": 0, "paid_count": 0, "vat": 20.0}]',
    '2022-05-04T08:28:30+00:00'
),
(
    'transaction_uuid__19',
    11,
    'canceled',
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 1, "in_pay_count": 0, "paid_count": 0, "vat": 20.0}]',
    '2022-05-04T08:20:30+00:00'
),
(
    'transaction_uuid__20',
    12,
    'canceled',
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 1, "in_pay_count": 0, "paid_count": 0, "vat": 20.0}]',
    '2022-05-04T08:29:30+00:00'
),
(
    'transaction_uuid__21',
    12,
    'canceled',
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 1, "in_pay_count": 0, "paid_count": 0, "vat": 20.0}]',
    '2022-05-04T06:28:30+00:00'
)
