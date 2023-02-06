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
    'test1_yql_shred_link',
    'test1_yt_table',
    ('{"size": 2000}')::jsonb,
    'Share',
    20,
    '2019-11-20 01:00:00'
),
(
    2,
    'test2_yql_shred_link',
    'test2_yt_table',
    ('{"size": 2000}')::jsonb,
    'Filter',
    10,
    '2019-11-20 01:00:00'
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
    created_at,
    segment_id
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
    '2021-03-12 01:00:00',
    1
),
(
    2,
    'name',
    'Driver',
    'trend',
    True,
    'NEW',
    'salt',
    '2021-03-12 01:00:00',
    2
);
