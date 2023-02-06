 INSERT INTO orders (uuid, table_id, service_fee, items, items_hash, status, eats_user_id, created_at)
 VALUES (
    'order_uuid__in_progress',
    1,
    9.0,
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 2, "in_pay_count": 0, "paid_count": 0, "vat": 20.0}]',
    '-831397301969266000',
    'new',
    '123',
    '2022-02-02 02:00:00Z'
),
(
    'order_uuid__error',
    1,
    9.0,
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 2, "in_pay_count": 0, "paid_count": 0, "vat": 20.0}]',
    '-831397301969266000',
    'creation_error',
    '123',
    '2022-02-02 02:00:00Z'
),
(
    'order_uuid__old_in_progress',
    1,
    9.0,
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 2, "in_pay_count": 0, "paid_count": 0, "vat": 20.0}]',
    '-831397301969266000',
    'new',
    '123',
    '2022-02-02 00:00:00Z'
),
(
    'order_uuid__old_error',
    1,
    9.0,
    '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1, "base_price": 0.1, "quantity": 2, "in_pay_count": 0, "paid_count": 0, "vat": 20.0}]',
    '-831397301969266000',
    'creation_error',
    '123',
    '2022-02-02 00:00:00Z'
);
