INSERT INTO crm_admin.segment
(
    id,
    yql_shared_url,
    yt_table,
    aggregate_info,
    mode,
    control,
    created_at
)
VALUES
(
    1,
    'yql_shared_link',
    'yt_table',
    ('{"size": 2000}')::jsonb,
    'Value',
    20,
    '2020-09-09 01:00:00'
),
(
    2,
    'yql_shared_link',
    'yt_table',
    ('{"size": 1000}')::jsonb,
    'Share',
    10,
    '2020-09-09 01:00:00'
),
(
    3,
    'yql_shared_link',
    'yt_table',
    ('{"size": 1000}')::jsonb,
    'Filter',
    10,
    '2020-09-09 01:00:00'
),
(
    4,
    'yql_shared_link',
    'yt_table',
    ('{"size": 1000}')::jsonb,
    'Value',
    10,
    '2020-09-09 01:00:00'
);

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
    ('{"channel_name": "user_sms", "content": "Hello!", "intent": "intent", "sender": "sender"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    2,  -- id
    'creative 2',
    ('{"channel_name": "user_sms", "content": "Hello!", "intent": "intent", "sender": "sender"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    3,  -- id
    'creative 3',
    ('{"channel_name": "user_sms", "content": "Hello!", "intent": "intent", "sender": "sender"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    4,  -- id
    'creative 4',
    ('{"channel_name": "user_sms", "content": "Hello!", "intent": "intent", "sender": "sender"}')::jsonb,
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
    ('{"channel_name": "user_sms", "content": "Hello!", "intent": "intent", "sender": "sender"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    7,  -- id
    'creative 7',
    ('{"channel_name": "user_sms", "content": "Hello!", "intent": "intent", "sender": "sender"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    8,  -- id
    'creative 8',
    ('{"channel_name": "user_sms", "content": "Hello!", "intent": "intent", "sender": "sender"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
);

INSERT INTO crm_admin.group_v2
(
    -- id,
    segment_id,
    creative_id,
    name,
    type,
    params,
    created_at,
    updated_at,
    send_at,
    sent_time,
    sending_stats
)
VALUES
(
    -- 1,  -- id
    2,
    1,
    'Only update, share 1',
    'SHARE',
    ('{"share": 10}')::jsonb,
    '2020-09-09 01:00:00',
    '2020-09-09 01:00:00',
    '2019-11-26 01:00:00',
    '2021-01-20T16:40:00',
    ('{"planned": 100}')::jsonb
),
(
    -- 2,  -- id
    2,
    2,
    'Only update, share 2',
    'SHARE',
    ('{"share": 10}')::jsonb,
    '2020-09-09 01:00:00',
    '2020-09-09 01:00:00',
    '2019-11-26 01:00:00',
    '2021-01-20T16:40:00',
    ('{"planned": 100}')::jsonb
),
(
    -- 3,  -- id
    3,
    3,
    'Update and save, filter 1',
    'FILTER',
    ('{"cities": ["Москва", "Орел"], "limit": 1000, "locales": ["RU"]}')::jsonb,
    '2020-09-09 01:00:00',
    '2020-09-09 01:00:00',
    '2019-11-26 01:00:00',
    '2021-01-20T16:40:00',
    ('{"planned": 100}')::jsonb
),
(
    -- 4,  -- id
    3,
    4,
    'Update and save, filter 2',
    'FILTER',
    ('{"cities": ["Москва", "Орел"], "limit": 1000, "locales": ["RU"]}')::jsonb,
    '2020-09-09 01:00:00',
    '2020-09-09 01:00:00',
    '2019-11-26 01:00:00',
    '2021-01-20T16:40:00',
    ('{"planned": 100}')::jsonb
),
(
    -- 5,  -- id
    4,
    5,
    'Update, save and delete, value 1',
    'VALUE',
    ('{"column": "column", "limit": 100, "values": ["1", "2"]}')::jsonb,
    '2020-09-09 01:00:00',
    '2020-09-09 01:00:00',
    '2019-11-26 01:00:00',
    '2021-01-20T16:40:00',
    ('{"planned": 100}')::jsonb
),
(
    -- 6,  -- id
    4,
    6,
    'Update, save and delete, value 2',
    'VALUE',
    ('{"column": "column", "limit": 100, "values": ["1", "2"]}')::jsonb,
    '2020-09-09 01:00:00',
    '2020-09-09 01:00:00',
    '2019-11-26 01:00:00',
    '2021-01-20T16:40:00',
    ('{"planned": 100}')::jsonb
),
(
    -- 7,  -- id
    4,
    7,
    'Update, save and delete, value 3',
    'VALUE',
    ('{"column": "column", "limit": 100, "values": ["1", "2"]}')::jsonb,
    '2020-09-09 01:00:00',
    '2020-09-09 01:00:00',
    '2019-11-26 01:00:00',
    '2021-01-20T16:40:00',
    ('{"planned": 100}')::jsonb
),
(
    -- 8,  -- id
    4,
    8,
    'Update, save and delete, value 4',
    'VALUE',
    ('{"column": "column", "limit": 100, "values": ["1", "2"]}')::jsonb,
    '2020-09-09 01:00:00',
    '2020-09-09 01:00:00',
    '2019-11-26 01:00:00',
    '2021-01-20T16:40:00',
    ('{"planned": 100}')::jsonb
);

INSERT INTO crm_admin.campaign
(
    id,
    segment_id,
    name,
    entity_type,
    trend,
    kind,
    discount,
    state,
    owner_name,
    ticket,
    ticket_status,
    created_at,
    updated_at,
    efficiency,
    efficiency_start_time,
    efficiency_stop_time
)
VALUES
(
    1,
    1,
    'campaign #1',
    'Driver',
    'trend',
    'kind',
    True,
    'GROUPS_READY',
    'user',
    'ticket',
    'open',
    '2020-09-09 01:00:00',
    '2020-09-09 01:00:00',
    false,
    NULL,
    NULL
),
(
    2,
    2,
    'campaign #2',
    'Driver',
    'trend',
    'kind',
    True,
    'GROUPS_READY',
    'user',
    'ticket',
    'open',
    '2020-09-09 01:00:00',
    '2020-09-09 01:00:00',
    false,
    NULL,
    NULL
),
(
    3,
    3,
    'campaign #3',
    'User',
    'trend',
    'kind',
    True,
    'GROUPS_READY',
    'user',
    'ticket',
    'open',
    '2020-09-09 01:00:00',
    '2020-09-09 01:00:00',
    false,
    NULL,
    NULL
),
(
    4,
    4,
    'campaign #4',
    'User',
    'trend',
    'kind',
    True,
    'GROUPS_READY',
    'user',
    'ticket',
    'open',
    '2020-09-09 01:00:00',
    '2020-09-09 01:00:00',
    true,
    '2020-09-09 01:00:00',
    '2020-09-10 02:00:00'
),
(
    5,
    NULL,
    'campaign #5',
    'User',
    'trend',
    'kind',
    True,
    'GROUPS_READY',
    'user',
    'ticket',
    'open',
    '2020-09-09 01:00:00',
    '2020-09-09 01:00:00',
    false,
    NULL,
    NULL
);
