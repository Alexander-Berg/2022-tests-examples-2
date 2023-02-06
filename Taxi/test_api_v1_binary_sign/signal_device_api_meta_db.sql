INSERT INTO signal_device_api.binary_sign_keys (
    client_id,
    api_key_hash,
    times_used,
    times_used_limit,
    is_active,
    created_at,
    updated_at
) VALUES (
    '12345',
    '320c3da5d4a8a81836afc70a00195064b9c1a53c6015812431a832371be8b487', -- DEADBEEF
    5,
    10,
    FALSE,
    TO_TIMESTAMP('2018-03-31 9:30:20','YYYY-MM-DD HH:MI:SS'),
    TO_TIMESTAMP('2018-03-31 9:30:20','YYYY-MM-DD HH:MI:SS')),
(
    '12345',
    '586208f59b45d3f2511316f3b273f32179846b0d5796c137920de23e810a496c', -- OLDBEEF
    0,
    10,
    TRUE,
    TO_TIMESTAMP('2017-03-31 9:30:20','YYYY-MM-DD HH:MI:SS'),
    TO_TIMESTAMP('2017-03-31 9:30:20','YYYY-MM-DD HH:MI:SS')),
(
    '12345',
    '0e34459a4f902615dd68417ee2c43a93eb53c673a2f8dfa32e4a440d77346cd2', -- BEEF
    9,
    10,
    TRUE,
    TO_TIMESTAMP('2020-03-31 9:30:20','YYYY-MM-DD HH:MI:SS'),
    TO_TIMESTAMP('2020-03-31 9:30:20','YYYY-MM-DD HH:MI:SS')
);
