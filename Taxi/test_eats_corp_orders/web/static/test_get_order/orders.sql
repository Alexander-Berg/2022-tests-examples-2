INSERT INTO orders
(
    id,
    status,
    idempotency_key,
    terminal_id,
    user_id,
    cancel_token,
    items,
    created_at,
    place_id
)
VALUES
(
    'order_id',
    'new',
    'idempotency_key',
    'terminal_id',
    177043222,
    'cancel_token',
    '[{"tin": "", "vat": "nds_0", "price": "60", "title": "Шоколад Bounty 55г", "quantity": "1"}]',
    '2020-02-02T03:00:00',
    '146'
);
