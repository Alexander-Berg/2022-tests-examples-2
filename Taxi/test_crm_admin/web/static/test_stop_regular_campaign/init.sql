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
    created_at
)
VALUES
(
    1,  -- id
    1,  -- segment_id
    'campaign #1',
    'User',
    'trend',
    True,
    'READY',
    True,  -- is_regular
    True,  -- is_active
    '2021-02-03 01:00:00'
),
(
    2,  -- id
    1,  -- segment_id
    'campaign #2',
    'Driver',
    'trend',
    True,
    'SENDING_PROCESSING',
    True,  -- is_regular
    True,  -- is_active
    '2021-02-03 01:00:00'
),
(
    3,  -- id
    1,  -- segment_id
    'campaign #3',
    'User',
    'trend',
    True,
    'READY',
    False,  -- is_regular
    False,  -- is_active
    '2021-02-03 01:00:00'
),
(
    4,  -- id
    1,  -- segment_id
    'campaign #4',
    'User',
    'trend',
    True,
    'READY',
    True,  -- is_regular
    False,  -- is_active
    '2021-02-03 01:00:00'
);
