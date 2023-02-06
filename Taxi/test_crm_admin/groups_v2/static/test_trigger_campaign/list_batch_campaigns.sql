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
    ('{"channel_name": "driver_push", "code": 1300, "content": "push"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    2,  -- id
    'creative 2',
    ('{"channel_name": "driver_wall", "content": "feed"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    3,  -- id
    'creative 3',
    ('{"channel_name": "driver_sms", "content": "sms"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    4,  -- id
    'creative 4',
    ('{"channel_name": "user_promo_fs", "content": "promo.fs"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
);

INSERT INTO crm_admin.group_v2
(
    id,
    name,
    creative_id,
    segment_id,
    type,
    params,
    send_at,
    created_at,
    updated_at
)
VALUES
(
    1,
    'group_1',
    1,
    1,
    'SHARE',
    ('{"share": 20}')::jsonb,
    '2020-09-09T04:00:00+03:00',
    '2020-09-09 01:00:00',
    '2020-09-09 01:00:00'
),
(
    2,
    'group_2',
    2,
    1,
    'SHARE',
    ('{"share": 10}')::jsonb,
    '2020-09-20T04:00:00+03:00',
    '2020-09-09 01:00:00',
    '2020-09-09 01:00:00'
),
(
    3,
    'group_3',
    3,
    2,
    'SHARE',
    ('{"share": 10}')::jsonb,
    '2020-09-20T04:00:00+03:00',
    '2020-09-09 01:00:00',
    '2020-09-09 01:00:00'
),
(
    4,
    'group_4',
    4,
    3,
    'SHARE',
    ('{"share": 10}')::jsonb,
    '2020-09-20T04:00:00+03:00',
    '2020-09-09 01:00:00',
    '2020-09-09 01:00:00'
),
(
    5,
    'group_5',
    Null,
    4,
    'SHARE',
    ('{"share": 10}')::jsonb,
    Null,
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
