INSERT INTO crm_admin.segment
(
    id,
    yql_shared_url,
    yt_table,
    mode,
    control,
    created_at
)
VALUES
(
    1,
    'yql_shared_url',
    'path/to/segment',
    'Share',
    20,
    '2021-02-03 01:00:00'
),
(
    10,
    'yql_shared_url',
    'path/to/segment',
    'Share',
    20,
    '2021-02-03 01:00:00'
),
(
    11,
    'yql_shared_url',
    'path/to/segment',
    'Share',
    20,
    '2021-02-03 01:00:00'
),
(
    12,
    'yql_shared_url',
    'path/to/segment',
    'Share',
    20,
    '2021-02-03 01:00:00'
);


INSERT INTO crm_admin.group
(
    id,
    segment_id,
    params,
    yql_shared_url,
    created_at,
    updated_at
)
VALUES
(
    1,
    1,
    ('{"name": "group_1", "state": "NEW", "share": 20, "channel": "PUSH", "content": "push message"}')::jsonb,
    'yql_shared_url',
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    10,
    10,
    ('{"name": "group_1", "state": "NEW", "share": 20, "channel": "DEVNULL", "content": "push message"}')::jsonb,
    'yql_shared_url',
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    11,
    11,
    ('{"name": "group_1", "state": "NEW", "share": 20, "channel": "DEVNULL", "content": "push message"}')::jsonb,
    'yql_shared_url',
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    12,
    11,
    ('{"name": "group_1", "state": "NEW", "share": 20, "channel": "PUSH", "content": "push message"}')::jsonb,
    'yql_shared_url',
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    13,
    12,
    ('{"name": "group_1", "state": "NEW", "share": 20, "content": "push message"}')::jsonb,
    'yql_shared_url',
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
);


INSERT INTO crm_admin.campaign
(
    id,
    segment_id,
    name,
    entity_type,
    trend,
    discount,
    state,
    is_regular,
    is_active,
    created_at,
    regular_start_time,
    regular_stop_time,
    efficiency_start_time,
    efficiency_stop_time
)
VALUES
(
    1,  -- id
    1,  -- segment_id
    'campaign #1',
    'User',
    'trend',
    True,
    'CAMPAIGN_APPROVED',
    True,  -- is_regular
    False,  -- is_active
    '2021-02-03 01:00:00',
    '2021-01-03 01:00:00',
    '2021-09-03 01:00:00',
    Null,
    Null
),
(
    2,  -- id
    1,  -- segment_id
    'campaign #2',
    'Driver',
    'trend',
    True,
    'STOPPED',
    True,  -- is_regular
    False,  -- is_active
    '2021-02-03 01:00:00',
    '2021-01-03 01:00:00',
    '2021-09-03 01:00:00',
    Null,
    Null
),
(
    3,  -- id
    1,  -- segment_id
    'campaign #3',
    'User',
    'trend',
    True,
    'READY',
    True,  -- is_regular
    True,  -- is_active
    '2021-02-03 01:00:00',
    '2021-01-03 01:00:00',
    '2021-09-03 01:00:00',
    Null,
    Null
),
(
    4,  -- id
    1,  -- segment_id
    'campaign #4',
    'User',
    'trend',
    True,
    'READY',
    False,  -- is_regular
    False,  -- is_active
    '2021-02-03 01:00:00',
    '2021-01-03 01:00:00',
    '2021-09-03 01:00:00',
    '2021-01-03 01:00:00',
    '2021-09-03 01:00:00'
),
(
    5,  -- id
    1,  -- segment_id
    'campaign #5',
    'User',
    'trend',
    True,
    'READY',
    True,  -- is_regular
    False,  -- is_active
    '2021-02-03 01:00:00',
    '2021-01-03 01:00:00',
    '2021-09-03 01:00:00',
    Null,
    Null
),
(
    10,  -- id
    10,  -- segment_id
    'campaign #10',
    'User',
    'trend',
    True,
    'CAMPAIGN_APPROVED',
    True,  -- is_regular
    False,  -- is_active
    '2021-02-03 01:00:00',
    '2021-01-03 01:00:00',
    '2021-09-03 01:00:00',
    Null,
    Null
),
(
    11,  -- id
    11,  -- segment_id
    'campaign #11',
    'User',
    'trend',
    True,
    'CAMPAIGN_APPROVED',
    True,  -- is_regular
    False,  -- is_active
    '2021-02-03 01:00:00',
    '2021-01-03 01:00:00',
    '2021-09-03 01:00:00',
    Null,
    Null
),
(
    12,  -- id
    12,  -- segment_id
    'campaign #12',
    'User',
    'trend',
    True,
    'CAMPAIGN_APPROVED',
    True,  -- is_regular
    False,  -- is_active
    '2021-02-03 01:00:00',
    '2021-01-03 01:00:00',
    '2021-09-03 01:00:00',
    Null,
    Null
);
