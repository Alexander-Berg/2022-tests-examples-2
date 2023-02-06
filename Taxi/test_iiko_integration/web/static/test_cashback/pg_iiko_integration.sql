INSERT INTO iiko_integration.orders
    (id, user_id, restaurant_order_id, invoice_id, idempotency_token, restaurant_id, expected_cashback_percentage, status, total_price, discount, currency, items, complement_payment_method_type, complement_payment_method_id)
VALUES
    ('1', 'user1', '123', 'one_percent_cashback', '01', 'restaurant01', 1, ('PENDING', 'HOLDING', now(),now()), 100, 0, 'RUB', ARRAY[]::ORDER_ITEM[], null, null),
    ('2', 'user1', '123', 'no_cashback',          '02', 'restaurant01', 0, ('PENDING', 'HOLDING', now(),now()), 100, 0, 'RUB', ARRAY[]::ORDER_ITEM[], null, null),
	('3', 'user1', '123', 'with_complement', '03', 'restaurant01', 1, ('PENDING', 'HOLDING', now(),now()), 100, 0, 'RUB', ARRAY[]::ORDER_ITEM[], 'personal_wallet', 'wallet-123');

