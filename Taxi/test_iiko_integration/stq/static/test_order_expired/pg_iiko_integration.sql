INSERT INTO iiko_integration.orders
    (id, invoice_id, restaurant_order_id, yandex_uid, status, created_at, idempotency_token, restaurant_id, expected_cashback_percentage, total_price, discount, currency, items, complement_amount, complement_payment_method_id, complement_payment_method_type)
VALUES
    ('01', 'invoice_01', '123', 'user1', ('WAITING_FOR_CONFIRMATION','HELD', now(),now()), '2020-06-07T09:05:00+00:00'::timestamptz, '01', 'restaurant01', 1, 100, 0, 'RUB', ARRAY[]::ORDER_ITEM[], null, null, null),
    ('02', 'invoice_02', '123', 'user1', ('PAYMENT_CONFIRMED','CLEARED', now(),now()),     '2020-06-02T09:00:00+00:00'::timestamptz, '02', 'restaurant01', 1, 700, 0, 'RUB', ARRAY[]::ORDER_ITEM[], null, null, null),
    ('03', 'invoice_03', '123', 'user1', ('PENDING','INIT', now(),now()),     '2020-06-02T09:00:00+00:00'::timestamptz, '03', 'restaurant01', 1, 700, 0, 'RUB', ARRAY[]::ORDER_ITEM[], null, null, null),
    ('04', 'invoice_04', '123', 'user1', ('PENDING','HOLDING', now(),now()),     '2020-06-02T09:00:00+00:00'::timestamptz, '04', 'restaurant01', 1, 700, 0, 'RUB', ARRAY[]::ORDER_ITEM[], null, null, null);
