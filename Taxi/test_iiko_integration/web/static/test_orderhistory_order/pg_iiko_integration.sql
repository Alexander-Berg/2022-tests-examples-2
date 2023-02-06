INSERT INTO iiko_integration.orders
    (id, restaurant_order_id, yandex_uid, status, created_at, idempotency_token, restaurant_id, expected_cashback_percentage, total_price, discount, currency, payment_method_type, payment_method_id, items)
VALUES
    ('01', '123', 'user1', ('PAYMENT_CONFIRMED', 'CLEARED', now(),now()), '2020-06-11T09:05:00+00:00'::timestamptz, '01', 'restaurant01', 5, 100, 0, 'RUB', 'card', 'some_card_id', ARRAY[
            ('01', NULL, 'product01',   2,  50, 100, 100,  0,  0, 16.67, 20, 1, NULL),
            ('02', NULL, 'product02', 0.5, 200, 125, 100, 25, 20,    20, 25, 2, NULL)
        ]::ORDER_ITEM[]),
    ('not_confirmed', '123', 'user1', ('WAITING_FOR_CONFIRMATION', 'CLEARED', now(),now()), '2020-06-11T09:05:00+00:00'::timestamptz, 'not_confirmed', 'restaurant01', 5, 100, 0, 'RUB', 'card', 'some_card_id', ARRAY[
            ('01', NULL, 'product01',   2,  50, 100, 100,  0,  0, 16.67, 20, 1, NULL),
            ('02', NULL, 'product02', 0.5, 200, 125, 100, 25, 20,    20, 25, 2, NULL)
        ]::ORDER_ITEM[]);

INSERT INTO iiko_integration.receipts (document_id, order_version, order_id, type, sum, url)
VALUES 
    ('d01', 1, '01', 'refund', 25.25, 'https://taxi-iiko-integration.s3.yandex.net/d01'),
    ('d00', 0, '01', 'payment', 150.5, 'https://taxi-iiko-integration.s3.yandex.net/d00'),
    ('d02', 2, '01', 'refund', 25.25, 'https://taxi-iiko-integration.s3.yandex.net/d02');
