INSERT INTO orders
(
    id,
    status,
    idempotency_key,
    terminal_id,
    user_id,
    cancel_token,
    items,
    meta_info,
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
    '{"user_overspending_enabled": true, "place_overspending_enabled": true, "payment_type": {"payment_method": {"type": "corp", "id": "corp:916880dd88914f3b836e1a289484c834:RUB"}}, "users_limits": [{"id": "916880dd88914f3b836e1a289484c834", "client_id": "00-00-00", "client_name": "Yandex Badge", "limits": [{"limit_id": "0-0-0", "currency": "RUB", "currency_sign": "p", "balance": "500", "value": "1000", "period": "day"}]}]}',
    '2020-02-02T03:00:00',
    '146'
);


INSERT INTO places
(
    place_id,
    balance_client_id,
    name,
    region_id,
    address_city,
    address_short,
    address_comment,
    brand_id,
    brand_name,
    location
)
VALUES
(
    '146',
    '',
    'Place name',
    '1',
    '',
    '',
    '',
    '777',
    'Brand name',
    '(37,55)'
);
