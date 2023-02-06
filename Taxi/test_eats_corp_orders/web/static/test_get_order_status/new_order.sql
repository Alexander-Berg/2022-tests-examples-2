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
    is_confirmation_required,
    amount
)
VALUES
(
    'order_id',
    'new',
    'idempotency_key',
    'terminal_id',
    177043222,
    'cancel_token',
    '[
        {"tin": "", "vat": "nds_0", "price": "10000.0", "title": "Мороженое", "quantity": "1.0"},
        {"tin": "", "vat": "nds_0", "price": "0.5", "title": "Дорогое мороженое", "quantity": "20000"}
    ]',
    '2020-02-02T03:00:00',
    false,
    20000
);
