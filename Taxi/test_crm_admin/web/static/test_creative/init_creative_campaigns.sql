INSERT INTO crm_admin.creative
(
    id,
    name,
    params,
    created_at,
    updated_at
)
VALUES
(
    1,  -- id
    'creative 1',
    ('{"channel_name": "driver_sms", "content": "Hello!", "intent": "intent", "sender": "sender"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    2,  -- id
    'creative 2',
    ('{"channel_name": "driver_push", "code": 100, "content": "Hello!"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    3,  -- id
    'creative 3',
    ('{"channel_name": "driver_push", "code": 1300, "content": "Hello!"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    4,  -- id
    'creative 4',
    ('{"channel_name": "driver_wall", "days_count": 1, "feed_id": "abc", "time_until": "10:00"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    5,  -- id
    'creative 5',
    ('{"channel_name": "user_sms", "content": "Hello!", "intent": "intent", "sender": "sender"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    6,  -- id
    'creative 6',
    ('{"channel_name": "user_push", "content": "Hello!"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    7,  -- id
    'creative 7',
    ('{"channel_name": "user_promo_fs", "content": "Hello!", "days_count": 1, "time_until": "10:00"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    8,  -- id
    'creative 8',
    ('{"channel_name": "eatsuser_sms", "content": "Hello!", "intent": "intent", "sender": "sender"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    9,  -- id
    'creative 9',
    ('{"channel_name": "eatsuser_push", "content": "Hello!"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    10,  -- id
    'creative 10',
    ('{"channel_name": "lavkauser_sms", "content": "Hello!", "intent": "intent", "sender": "sender"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    11,  -- id
    'creative 11',
    ('{"channel_name": "lavkauser_push", "content": "Hello!"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
);

INSERT INTO crm_admin.campaign
(
    id,
    name,
    entity_type,
    trend,
    discount,
    state,
    salt,
    created_at
)
VALUES
(
    1,
    'name',
    'User',
    'trend',
    True,
    'NEW',
    'salt',
    '2021-03-12 01:00:00'
),
(
    2,
    'name',
    'User',
    'trend',
    True,
    'NEW',
    'salt',
    '2021-03-12 01:00:00'
),
(
    3,
    'name',
    'User',
    'trend',
    True,
    'NEW',
    'salt',
    '2021-03-12 01:00:00'
);

INSERT INTO crm_admin.campaign_creative_connection
(
    id,
    campaign_id,
    creative_id,
    created_at
)
VALUES
(
    1,
    1,
    1,
    '2021-03-12 01:00:00'
),
(
    2,
    2,
    2,
    '2021-03-12 01:00:00'
),
(
    3,
    3,
    3,
    '2021-03-12 01:00:00'
),
(
    4,
    1,
    4,
    '2021-03-12 01:00:00'
),
(
    5,
    1,
    5,
    '2021-03-12 01:00:00'
),
(
    6,
    2,
    6,
    '2021-03-12 01:00:00'
),
(
    7,
    2,
    7,
    '2021-03-12 01:00:00'
),
(
    8,
    3,
    8,
    '2021-03-12 01:00:00'
),
(
    9,
    3,
    9,
    '2021-03-12 01:00:00'
),
(
    10,
    3,
    10,
    '2021-03-12 01:00:00'
),
(
    11,
    3,
    11,
    '2021-03-12 01:00:00'
);
