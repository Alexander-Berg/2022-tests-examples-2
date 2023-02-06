INSERT INTO fleet_notifications_telegram_bot.tg_users_info
(
    receiver,
    registered_with_token,
    telegram_pd_id,
    last_message_id
)
VALUES
(
    ('p1', '1'),
    't3',
    'pd1',
    'it2222222222222222222222'
),
(
    ('p1', '2'),
    't4',
    'pd2',
    NULL
),
(
    ('p1', '3'),
    't5',
    'pd1',
    NULL
);

INSERT INTO fleet_notifications_telegram_bot.identification_tokens_info
(
    identification_token,
    receiver,
    identification_token_valid_until
)
VALUES
(
    't1',
    ('p1', '4'),
    '2020-11-12T00:00:00+03:00'
),
(
    't2',
    ('p1', '5'),
    NOW() + '5 HOURS'::INTERVAL
);
