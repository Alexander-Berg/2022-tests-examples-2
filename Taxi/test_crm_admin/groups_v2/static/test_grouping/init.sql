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
    'segment#1 shared link',
    'path/to/segment_1',
    ('{
        "size": 2000,
        "distribution": [
            {
                "city": "Moscow",
                "locales": [
                    { "name": "ru", "value": 1000 },
                    { "name": "en", "value": 500 }
                ]
            },
            {
                "city": "Saint Petersburg",
                "locales": [
                    { "name": "ru", "value": 500 },
                    { "name": "en", "value": 1000 }
                ]
            }
        ]
    }')::jsonb,
    'Share',
    20,
    '2020-06-09 01:00:00'
),
(
    2,
    'segment#2 shared link',
    'path/to/segment_2',
    ('{
        "size": 2000,
        "distribution": [
            {
                "city": "Moscow",
                "locales": [
                    { "name": "ru", "value": 1000 },
                    { "name": "en", "value": 500 }
                ]
            },
            {
                "city": "Saint Petersburg",
                "locales": [
                    { "name": "ru", "value": 500 },
                    { "name": "en", "value": 1000 }
                ]
            }
        ]
    }')::jsonb,
    'Filter',
    20,
    '2020-06-09 01:00:00'
),
(
    3,
    'segment#3 shared link',
    'path/to/segment_3',
    null,
    'Share',
    20,
    '2020-08-20 01:00:00'
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
    ('{"channel_name": "user_push", "content": "push text"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    2,  -- id
    'creative 2',
    ('{"channel_name": "user_push", "content": "push text"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    3,  -- id
    'creative 3',
    ('{"channel_name": "user_push", "content": "push text"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    4,  -- id
    'creative 4',
    ('{"channel_name": "user_push", "content": "push text"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    5,  -- id
    'creative 5',
    ('{"channel_name": "user_push", "content": "push text"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    6,  -- id
    'creative 6',
    ('{"channel_name": "driver_push", "code": 1300, "content": "push text"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    7,  -- id
    'creative 7',
    ('{"channel_name": "driver_push", "code": 1300, "content": "push text"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
);

INSERT INTO crm_admin.group_v2
(
    creative_id,
    segment_id,
    name,
    type,
    params,
    send_at,
    created_at,
    updated_at
)
VALUES
(
    1,
    1,
    'share_group_1',
    'SHARE',
    ('{"share": 20}')::jsonb,
    '2019-11-20T01:00:00',
    '2020-06-09 01:00:00',
    '2020-06-09 01:00:00'
),
(
    2,
    1,
    'share_group_2',
    'SHARE',
    ('{"share": 10}')::jsonb,
    '2019-11-20T01:00:00',
    '2020-06-09 01:00:00',
    '2020-06-09 01:00:00'
),
(
    3,
    2,
    'filter_group_1',
    'FILTER',
    ('{"cities": ["Moscow"], "limit": 100, "locales": []}')::jsonb,
    null,
    '2020-06-09 01:00:00',
    '2020-06-09 01:00:00'
),
(
    4,
    2,
    'filter_group_2',
    'FILTER',
    ('{"cities": ["Moscow", "Saint Petersburg"], "limit": 100, "locales": ["ru"]}')::jsonb,
    null,
    '2020-06-09 01:00:00',
    '2020-06-09 01:00:00'
),
(
    5,
    2,
    'filter_group_3',
    'FILTER',
    ('{"cities": ["Moscow", "Saint Petersburg"], "limit": 100, "locales": ["en"]}')::jsonb,
    null,
    '2020-06-09 01:00:00',
    '2020-06-09 01:00:00'
),
(
    6,
    3,
    'share_group_1',
    'SHARE',
    ('{"share": 20}')::jsonb,
    '2020-08-20T01:00:00',
    '2020-06-09 01:00:00',
    '2020-06-09 01:00:00'
),
(
    7,
    3,
    'share_group_2',
    'SHARE',
    ('{"share": 10}')::jsonb,
    '2020-08-20T01:00:00',
    '2020-06-09 01:00:00',
    '2020-06-09 01:00:00'
);


INSERT INTO crm_admin.campaign
(
    id,
    name,
    segment_id,
    entity_type,
    trend,
    kind,
    discount,
    state,
    owner_name,
    global_control,
    ticket,
    created_at
)
VALUES
(
    1,
    'campaing #1',
    1,
    'User',
    'campaign #1 trend',
    'campaign #1 kind',
    True,
    'GROUPS_PRECALCULATING',
    'user1',
    True,
    'ticket #1',
    '2020-04-01 01:00:00'
),
(
    2,
    'campaing #2',
    2,
    'User',
    'campaign #2 trend',
    'campaign #2 kind',
    True,
    'GROUPS_PRECALCULATING',
    'user2',
    False,
    'ticket #2',
    '2020-04-01 01:00:00'
),
(
    3,
    'campaing #3',
    Null,
    'User',
    'campaign #3 trend',
    'campaign #3 kind',
    True,
    'NEW',
    'user2',
    False,
    'ticket #3',
    '2020-04-01 01:00:00'
),
(
    4,
    'campaing #4',
    3,
    'Driver',
    'campaign #4 trend',
    'campaign #4 kind',
    True,
    'GROUPS_CALCULATING',
    'user2',
    False,
    'ticket #3',
    '2020-04-01 01:00:00'
);


INSERT INTO crm_admin.operations(
    campaign_id,
    operation_name,
    submission_id,
    operation_type,
    status,
    started_at,
    finished_at
)
VALUES
(
    -- id: 1
    1,  -- campaign_id
    'create groups',
    null, -- submission_id
    null, -- operation_type
    null, -- status
    '2020-10-26 02:00:00',
    null  -- finished_at
),
(
    -- id: 2
    2,  -- campaign_id
    'create groups',
    null, -- submission_id
    null, -- operation_type
    null, -- status
    '2020-10-26 02:00:00',
    null  -- finished_at
),
(
    -- id: 3
    1,  -- campaign_id
    'create groups',
    'submission_id',
    'spark',
    'RUNNING',
    '2020-10-26 02:00:00',
    '2020-10-26 03:00:00'
),
(
    -- id: 4
    4,  -- campaign_id
    'create groups',
    null, -- submission_id
    null, -- operation_type
    null, -- status
    '2020-10-26 02:00:00',
    null
);
