INSERT INTO user_codes
(
    user_id,
    code,
    qr_code,
    expires_at
)
VALUES
(
    177043222,
    '111111',
    'YNDX17bd2a3c7db44373822cc291d09b86bc',
    '2022-02-22 22:03:00.000000Z'
);

INSERT INTO terminal_tokens
(
    id,
    token,
    dek,
    place_id
)
VALUES
(
    'terminal_id',
    '6j3/BEioT3vgvNa9ca2U7e+DuO1dqEs9x8hShzbet/I=',
    'pbrXGGxr9JdNTEsQeCjss+gc/8S9hyYndVkxdNw0B5e3B0CV4WXAyCZZBcIP7aqxLRCql1nNVjeTXDBBNCYQYQ==',
    '146'
);

INSERT INTO orders
(
    id,
    status,
    idempotency_key,
    terminal_id,
    user_id,
    cancel_token,
    amount,
    order_nr
)
VALUES
(
    'order_id',
    'new',
    'idempotency_key',
    'terminal_id',
    177043222,
    'cancel_token',
    100.5,
    '00000-00000'
);
