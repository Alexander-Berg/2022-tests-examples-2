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
    ('{"name": "group1", "share": 10, "state": "NEW", "channel": "PUSH"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
);


INSERT INTO crm_admin.campaign
(
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
    -- id: 1
    1,  -- segment_id
    'oneshot campaign',
    'User',
    'trend',
    True,  -- discount
    'SCHEDULED',
    False,  -- is_regular
    False,  -- is_active
    '0 12 * * *',  -- schedule
    '2021-01-01T00:00:00',  -- regular_start_time
    '2021-10-31T00:00:00',  -- regular_stop_time
    '2021-01-26 01:00:00'
),
(
    -- id: 2
    1,  -- segment_id
    'regular campaign',
    'User',
    'trend',
    True,  -- discount
    'SCHEDULED',
    True,  -- is_regular
    True,  -- is_active
    '0 12 * * *',  -- schedule
    '2021-01-01T00:00:00',  -- regular_start_time
    '2021-10-31T00:00:00',  -- regular_stop_time
    '2021-01-26 01:00:00'
);
