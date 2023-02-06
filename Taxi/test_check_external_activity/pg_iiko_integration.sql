INSERT INTO iiko_integration.orders
    (id, restaurant_order_id, idempotency_token, restaurant_id, expected_cashback_percentage, status, created_at, total_price, discount, currency, items)
VALUES
    ('1',                '123', '01', 'restaurant01', 0, ('PENDING',                           'INIT',        '2020-01-01T00:00:00+00:00'::timestamptz, '2020-01-01T00:00:00+00:00'::timestamptz), '2020-01-01T00:00:00+00:00'::timestamptz, 100, 0, 'RUB', ARRAY[]::ORDER_ITEM[]),
    ('2',                '123', '02', 'restaurant01', 0, ('WAITING_FOR_CONFIRMATION',          'HELD',        '2020-01-01T00:00:00+00:00'::timestamptz, '2020-01-01T00:00:00+00:00'::timestamptz), '2020-01-01T00:00:00+00:00'::timestamptz, 100, 0, 'RUB', ARRAY[]::ORDER_ITEM[])
;


INSERT INTO iiko_integration.external_activity
    (order_id, last_activity_at)
VALUES
    ('1', NOW() - INTERVAL '10 seconds'),
    ('2', NOW() - INTERVAL '5 seconds')
;

INSERT INTO iiko_integration.cron_info
    (cron_id, last_run_at)
VALUES
    ('check_external_activity', '2020-01-01T00:00:00+00:00'::timestamptz)
;
