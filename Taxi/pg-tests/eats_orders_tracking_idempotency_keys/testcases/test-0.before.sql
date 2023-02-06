INSERT INTO eats_orders_tracking.idempotency_keys
(idempotency_key, created_at)
VALUES
    ('idempotency_key-1', '2022-07-17T12:00:00.0000+03:00'::TIMESTAMPTZ),
    ('idempotency_key-2', '2022-07-17T12:01:00.0000+03:00'::TIMESTAMPTZ);
