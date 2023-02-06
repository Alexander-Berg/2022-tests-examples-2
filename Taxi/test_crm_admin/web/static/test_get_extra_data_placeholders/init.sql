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
    1,  -- id
    'yql_shared_url',
    'segment_path',
    'Share',
    20,
    '2021-02-03 01:00:00'
),
(
    2,  -- id
    'yql_shared_url',
    'segment_path',
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
    extra_data_path,
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
    'APPROVED',
    'extra_data_path',
    '2021-02-03 01:00:00'
),
(
    2,  -- id
    2,  -- segment_id
    'campaign #2',
    'Driver',
    'trend',
    True,
    'APPROVED',
    null,
    '2021-02-03 01:00:00'
),
(
    3,  -- id
    null,  -- segment_id
    'campaign #3',
    'User',
    'trend',
    True,
    'APPROVED',
    null,
    '2021-02-03 01:00:00'
);
