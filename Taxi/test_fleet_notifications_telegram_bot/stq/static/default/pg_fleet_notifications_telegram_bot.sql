INSERT INTO fleet_notifications_telegram_bot.tg_users_info
(
    receiver,
    registered_with_token,
    telegram_pd_id
)
VALUES
(
    ('p1', 'u1'),
    'token1',
    'pd1'
);

INSERT INTO fleet_notifications_telegram_bot.identification_tokens_info
(
    identification_token,
    receiver,
    identification_token_valid_until
)
VALUES
(
    'token1',
    ('p1', 'u2'),
    NOW() + '5 hour'::INTERVAL
),
(
    'token2',
    ('p1', 'u4'),
    NOW() + '5 hour'::INTERVAL
),
(
    'token3',
    ('p1', 'u5'),
    NOW() - '5 hour'::INTERVAL
);
