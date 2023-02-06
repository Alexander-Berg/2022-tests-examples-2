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
    'yt_table',
    'Share',
    20,
    '2021-01-27 01:00:00'
),
(
    2,  -- id
    'yql_shared_url',
    'yt_table',
    'Share',
    20,
    '2021-01-27 01:00:00'
),
(
    3,  -- id
    'yql_shared_url',
    'yt_table',
    'Share',
    20,
    '2021-01-27 01:00:00'
),
(
    4,  -- id
    'yql_shared_url',
    'yt_table',
    'Share',
    20,
    '2021-01-27 01:00:00'
),
(
    5,  -- id
    'yql_shared_url',
    'yt_table',
    'Share',
    20,
    '2021-01-27 01:00:00'
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
    1,  -- id
    1,  -- segment_id
    ('{"name": "group1", "share": 10, "state": "NEW"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    2,  -- id
    1,  -- segment_id
    ('{"name": "group1", "share": 10, "state": "NEW"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    3,  -- id
    2,  -- segment_id
    ('{"name": "group1", "share": 10, "state": "NEW"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
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
    schedule,
    regular_start_time,
    regular_stop_time,
    created_at
)
VALUES
(
    1,  -- id
    1,  -- segment_id
    'ready for processing',
    'User',
    'trend',
    True,  -- discount
    'SCHEDULED',
    True,  -- is_regular
    True,  -- is_active
    '1 12 * * *',  -- schedule
    '2021-01-01 01:00:00',  -- regular_start_time
    '2021-12-31 01:00:00',  -- regular_stop_time
    '2021-01-26 01:00:00'
),
(
    2,  -- id
    2,  -- segment_id
    'not yet ready for processing',
    'Driver',
    'trend',
    True,  -- discount
    'SCHEDULED',
    True,  -- is_regular
    True,  -- is_active
    '0 13 * * *',  -- schedule
    '2021-01-01 01:00:00',  -- regular_start_time
    '2021-12-31 01:00:00',  -- regular_stop_time
    '2021-01-26 01:00:00'
),
(
    3,  -- id
    3,  -- segment_id
    'already queued',
    'Driver',
    'trend',
    True,  -- discount
    'SCHEDULED',
    True,  -- is_regular
    True,  -- is_active
    '1 12 * * *',  -- schedule
    '2021-01-01 01:00:00',  -- regular_start_time
    '2021-12-31 01:00:00',  -- regular_stop_time
    '2021-01-26 01:00:00'
),
(
    4,  -- id
    4,  -- segment_id
    'wrong state',
    'Driver',
    'trend',
    True,  -- discount
    'GROUPS_READY',
    True,  -- is_regular
    True,  -- is_active
    '1 12 * * *',  -- schedule
    '2021-01-01 01:00:00',  -- regular_start_time
    '2021-12-31 01:00:00',  -- regular_stop_time
    '2021-01-26 01:00:00'
),
(
    5,  -- id
    5,  -- segment_id
    'not regular',
    'Driver',
    'trend',
    True,  -- discount
    'SCHEDULED',
    False,  -- is_regular
    True,  -- is_active
    null,
    null,  -- regular_start_time
    null,  -- regular_stop_time
    '2021-01-26 01:00:00'
),
(
    6,  -- id
    5,  -- segment_id
    'not active',
    'Driver',
    'trend',
    True,  -- discount
    'SCHEDULED',
    True,  -- is_regular
    False,  -- is_active
    '1 12 * * *',  -- schedule
    '2021-01-01 01:00:00',  -- regular_start_time
    '2021-12-31 01:00:00',  -- regular_stop_time
    '2021-01-26 01:00:00'
),
(
    7,  -- id
    5,  -- segment_id
    'not a valid period',
    'Driver',
    'trend',
    True,  -- discount
    'SCHEDULED',
    True,  -- is_regular
    True,  -- is_active
    '1 12 * * *',  -- schedule
    '2022-01-01 01:00:00',  -- regular_start_time
    '2022-12-31 01:00:00',  -- regular_stop_time
    '2021-01-26 01:00:00'
),
(
    8,  -- id
    1,  -- segment_id
    'ready for processing',
    'User',
    'trend',
    True,  -- discount
    'SCHEDULED',
    True,  -- is_regular
    True,  -- is_active
    '1 12 * * *',  -- schedule
    '2021-01-01 01:00:00',  -- regular_start_time
    '2021-01-25 01:00:00',  -- regular_stop_time
    '2021-01-26 01:00:00'
);


INSERT INTO crm_admin.schedule
(
    campaign_id,
    scheduled_for
)
VALUES
(
    3,  -- campaign_id
    '2021-01-26 12:00:00'
);
