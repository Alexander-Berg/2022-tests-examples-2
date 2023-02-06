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
    3,
    'segment#3 shared link',
    'path/to/segment_3',
    null,
    'Share',
    20,
    '2020-08-20 01:00:00'
);


INSERT INTO crm_admin.group
(
    segment_id,
    params,
    created_at,
    updated_at
)
VALUES
(
    1,
    ('{"channel": "PUSH", "content": "push text", "name": "share_group_1", "share": 20, "send_at": "2019-11-20T04:00:00+03:00"}')::jsonb,
    '2020-06-09 01:00:00',
    '2020-06-09 01:00:00'
),
(
    1,
    ('{"channel": "PUSH", "content": "push text", "name": "share_group_2", "share": 10, "send_at": "2019-11-20T04:00:00+03:00"}')::jsonb,
    '2020-06-09 01:00:00',
    '2020-06-09 01:00:00'
),
(
    3,
    ('{"channel": "PUSH", "content": "push text", "name": "share_group_1", "share": 20, "send_at": "2020-08-20T04:00:00+03:00"}')::jsonb,
    '2020-06-09 01:00:00',
    '2020-06-09 01:00:00'
),
(
    3,
    ('{"channel": "PUSH", "content": "push text", "name": "share_group_2", "share": 10, "send_at": "2020-08-20T04:00:00+03:00"}')::jsonb,
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
    'GROUPS_CALCULATING',
    'user1',
    True,
    'ticket #1',
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
    retry_count,
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
    1,
    '2020-10-26 02:00:00',
    null  -- finished_at
),
(
    -- id: 2
    1,  -- campaign_id
    'create groups',
    'submission_id',
    'segment_splitter',
    'RUNNING',
    1,
    '2020-10-26 02:00:00',
    '2020-10-26 03:00:00'
),
(
    -- id: 3
    4,  -- campaign_id
    'create groups',
    null, -- submission_id
    null, -- operation_type
    null, -- status
    1,
    '2020-10-26 02:00:00',
    null
);
