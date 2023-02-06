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
    'yql_shred_link',
    'yt_table',
    ('{"size": 2000}')::jsonb,
    'Share',
    20,
    '2020-09-09 01:00:00'
),
(
    2,
    'yql_shred_link',
    'yt_table',
    ('{"size": 1000}')::jsonb,
    'Share',
    10,
    '2020-09-09 01:00:00'
),
(
    3,
    'yql_shred_link',
    'yt_table',
    ('{"size": 1000}')::jsonb,
    'Share',
    10,
    '2020-09-09 01:00:00'
),
(
    4,
    'yql_shred_link',
    'yt_table',
    ('{"size": 1000}')::jsonb,
    'Share',
    10,
    '2020-09-09 01:00:00'
);

INSERT INTO crm_admin.group
(
    id,
    segment_id,
    params,
    created_at,
    updated_at
)
VALUES
(
    1,
    1,
    ('{"channel": "PUSH", "content": "push", "name": "group_1", "share": 20, "send_at": "2020-09-09T04:00:00+03:00"}')::jsonb,
    '2020-09-09 01:00:00',
    '2020-09-09 01:00:00'
),
(
    2,
    1,
    ('{"channel": "FEED", "content": "feed", "name": "group_2", "share": 10, "send_at": "2020-09-20T04:00:00+03:00"}')::jsonb,
    '2020-09-09 01:00:00',
    '2020-09-09 01:00:00'
),
(
    3,
    2,
    ('{"channel": "SMS", "content": "sms", "name": "group_1", "share": 10, "send_at": "2020-09-20T04:00:00+03:00"}')::jsonb,
    '2020-09-09 01:00:00',
    '2020-09-09 01:00:00'
),
(
    4,
    3,
    ('{"channel": "promo.fs", "content": "promo.fs", "name": "group_1", "share": 10, "send_at": "2020-09-20T04:00:00+03:00"}')::jsonb,
    '2020-09-09 01:00:00',
    '2020-09-09 01:00:00'
),
(
    5,
    4,
    ('{}')::jsonb,
    '2020-09-09 01:00:00',
    '2020-09-09 01:00:00'
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
    updated_at
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
    'NEW',
    'user',
    'ticket',
    'open',
    '2020-09-09 01:00:00',
    '2020-09-09 01:00:00'
),
(
    2,
    2,
    'campaign #2',
    'Driver',
    'trend',
    'kind',
    True,
    'NEW',
    'user',
    'ticket',
    'open',
    '2020-09-09 01:00:00',
    '2020-09-09 01:00:00'
),
(
    3,
    3,
    'campaign #3',
    'User',
    'trend',
    'kind',
    True,
    'NEW',
    'user',
    'ticket',
    'open',
    '2020-09-09 01:00:00',
    '2020-09-09 01:00:00'
),
(
    4,
    4,
    'campaign #4',
    'User',
    'trend',
    'kind',
    True,
    'NEW',
    'user',
    'ticket',
    'open',
    '2020-09-09 01:00:00',
    '2020-09-09 01:00:00'
);
