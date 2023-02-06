INSERT INTO iiko_integration.orders
    (id, user_id, status, created_at, idempotency_token, restaurant_id, expected_cashback_percentage, total_price, discount, currency, items, restaurant_order_id, payment_method_id)
VALUES
    ('01',       'user', ('PAYMENT_CONFIRMED', 'CLEARED', '2020-06-02 09:00:00'::timestamp, '2020-06-02 09:00:00'::timestamp),  '2020-06-02 09:00:00'::timestamp, '01', 'restaurant01', 1, 100, 0, 'RUB', ARRAY[]::ORDER_ITEM[], 'iiko_01', 'card-01'),
    ('02',       'user', ('CANCELED', 'HOLD_FAILED', '2020-06-04 09:00:00'::timestamp, '2020-06-04 09:00:00'::timestamp), '2020-06-04 09:15:00'::timestamp, '02', 'restaurant01', 1, 100, 0, 'RUB', ARRAY[]::ORDER_ITEM[], 'iiko_02', 'card-02');
