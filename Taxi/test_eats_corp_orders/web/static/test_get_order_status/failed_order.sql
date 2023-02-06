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
    amount,
    error_code,
    error_message
)
VALUES
(
    'order_id',
    'failed',
    'idempotency_key',
    'terminal_id',
    177043222,
    'cancel_token',
    '[
        {"tin": "", "vat": "nds_0", "price": "1.0", "title": "Мороженое", "quantity": "2.0"},
        {"tin": "", "vat": "nds_0", "price": "5.0", "title": "Дорогое мороженое", "quantity": "0.5"},
        {"tin": "", "vat": "nds_0", "price": "5.0", "title": "Дорогое мороженое", "quantity": "0.5"}
    ]',
    '2020-02-02T03:00:00',
    false,
    7.0,
    'NOT_ENOUGH_BALANCE',
    'Not enough balance'
);
