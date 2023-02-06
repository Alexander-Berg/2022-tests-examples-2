INSERT INTO iiko_integration.orders
    (id, restaurant_order_id, idempotency_token, restaurant_id, expected_cashback_percentage, status, total_price, discount, currency, items)
VALUES
    ('01', '123', '01', 'restaurant01', 0, ('PENDING','INIT',now(),now()),                           100, 0, 'RUB', ARRAY[]::ORDER_ITEM[]),
    ('02', '123', '02', 'fakefakefake', 0, ('PENDING','INIT',now(),now()),                           100, 0, 'RUB', ARRAY[]::ORDER_ITEM[]),
    ('03', '123', '03', 'restaurant01', 0, ('CANCELED','INIT',now(),now()),            100, 0, 'RUB', ARRAY[]::ORDER_ITEM[]),
    ('04', '123', '04', 'restaurant01', 0, ('CLOSED','INIT',now(),now()),              100, 0, 'RUB', ARRAY[]::ORDER_ITEM[]),
    ('05', '123', '05', 'restaurant01', 0, ('PENDING','HOLDING',now(),now()),                        100, 0, 'RUB', ARRAY[]::ORDER_ITEM[]),
    ('06', '123', '06', 'restaurant01', 0, ('WAITING_FOR_CONFIRMATION', 'HELD', now(),now()),        100, 0, 'RUB', ARRAY[]::ORDER_ITEM[]),
    ('07', '123', '07', 'restaurant01', 0, ('PAYMENT_CONFIRMED','HELD',now(),now()),                         100, 0, 'RUB', ARRAY[]::ORDER_ITEM[]),
    ('08', '123', '08', 'restaurant01', 0, ('PENDING','HOLD_FAILED', now(),now()),  100, 0, 'RUB', ARRAY[]::ORDER_ITEM[]),
    ('09', '123', '09', 'restaurant01', 0, ('PAYMENT_CONFIRMED', 'CLEARING', now(),now()),                   100, 0, 'RUB', ARRAY[]::ORDER_ITEM[]),
    ('10', '123', '10', 'restaurant01', 0, ('PAYMENT_CONFIRMED', 'CLEARED', now(),now()),                    100, 0, 'RUB', ARRAY[]::ORDER_ITEM[]),
    ('11', '123', '11', 'restaurant01', 0, ('EXPIRED', 'CLEARED', now(),now()),                    100, 0, 'RUB', ARRAY[]::ORDER_ITEM[]);

