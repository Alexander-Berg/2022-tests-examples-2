INSERT INTO iiko_integration.receipts (document_id, order_version, order_id, type, sum, url)
    VALUES (
        'document_2',
        0,
        '000',
        'payment',
        219,
        'https://taxi-iiko-integration.s3.yandex.net/document_2'
    );

INSERT INTO iiko_integration.orders
    (id, restaurant_order_id, user_id, status, created_at, idempotency_token, restaurant_id, expected_cashback_percentage, total_price, discount, currency, items)
VALUES
    ('000', '123', 'user1', ('PAYMENT_CONFIRMED','CLEARED',now(), now()), '2020-06-11T09:05:00+00:00'::timestamptz, '01', 'restaurant01', 1, 100, 0, 'RUB', ARRAY[]::ORDER_ITEM[]);
