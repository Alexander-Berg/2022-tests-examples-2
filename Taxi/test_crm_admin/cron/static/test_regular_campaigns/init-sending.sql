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
    regular_start_time,
    regular_stop_time,
    schedule,
    created_at
)
VALUES
(
    1,  -- id
    1,  -- segment_id
    'active user campaign',
    'User',
    'trend',
    True,  -- discount
    'GROUPS_FINISHED',
    True,  -- is_regular
    True,  -- is_active
    '2021-01-01 01:00:00',  -- regular_start_time
    '2021-12-31 01:00:00',  -- regular_stop_time
    '0 12 * * *',  -- schedule
    '2021-01-26 01:00:00'
),
(
    2,  -- id
    1,  -- segment_id
    'active driver campaign',
    'Driver',
    'trend',
    True,  -- discount
    'GROUPS_FINISHED',
    True,  -- is_regular
    True,  -- is_active
    '2021-01-01 01:00:00',  -- regular_start_time
    '2021-12-31 01:00:00',  -- regular_stop_time
    '0 12 * * *',  -- schedule
    '2021-01-26 01:00:00'
),
(
    3,  -- id
    1,  -- segment_id
    'inactive',
    'Driver',
    'trend',
    True,  -- discount
    'GROUPS_FINISHED',
    True,  -- is_regular
    False,  -- is_active
    '2021-01-01 01:00:00',  -- regular_start_time
    '2021-12-31 01:00:00',  -- regular_stop_time
    '0 12 * * *',  -- schedule
    '2021-01-26 01:00:00'
),
(
    4,  -- id
    1,  -- segment_id
    'not ready for sending',
    'Driver',
    'trend',
    True,  -- discount
    'READY',
    True,  -- is_regular
    True,  -- is_active
    '2021-01-01 01:00:00',  -- regular_start_time
    '2021-12-31 01:00:00',  -- regular_stop_time
    '0 12 * * *',  -- schedule
    '2021-01-26 01:00:00'
),
(
    5,  -- id
    1,  -- segment_id
    'active user campaign',
    'User',
    'trend',
    True,  -- discount
    'GROUPS_FINISHED',
    True,  -- is_regular
    True,  -- is_active
    '2021-01-01 01:00:00',  -- regular_start_time
    '2021-01-25 01:00:00',  -- regular_stop_time
    '0 12 * * *',  -- schedule
    '2021-01-26 01:00:00'
);


INSERT INTO crm_admin.schedule
(
    id,
    campaign_id,
    scheduled_for
)
VALUES
(
    1,  -- id
    1,  -- campaign_id
    '2021-01-26 12:00:00'
),
(
    2,  -- id
    2,  -- campaign_id
    '2021-01-26 12:00:00'
),
(
    3,  -- id
    3,  -- campaign_id
    '2021-01-26 12:00:00'
),
(
    4,  -- id
    4,  -- campaign_id
    '2021-01-26 12:00:00'
),
(
    5,  -- id
    5,  -- campaign_id
    '2021-01-26 12:00:00'
);
