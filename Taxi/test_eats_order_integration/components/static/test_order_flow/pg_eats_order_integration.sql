INSERT INTO order_flow
(
    idempotency_key,
    is_locked,
    order_nr
)
values
(
    'idempotency_key_locked',
    true,
    'order-001'
),
(
    'idempotency_key_free',
    false,
    'order-002'
)
;
