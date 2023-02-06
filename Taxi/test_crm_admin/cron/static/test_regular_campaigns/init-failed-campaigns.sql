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
    created_at,
    root_id
)
VALUES
(
    1,  -- id
    1,  -- segment_id
    'idle campaign',
    'User',
    'trend',
    True,  -- discount
    'SCHEDULED',
    True,  -- is_regular
    True,  -- is_active
    '2021-01-01T12:00:00',  -- regular_start_time
    '2021-12-31T12:00:00',  -- regular_stop_time
    '2021-01-26 01:00:00',
    1
),
(
    2,  -- id
    1,  -- segment_id
    'failed campaign',
    'Driver',
    'trend',
    True,  -- discount
    'SEGMENT_ERROR',
    True,  -- is_regular
    True,  -- is_active
    '2021-01-01T12:00:00',  -- regular_start_time
    '2021-12-31T12:00:00',  -- regular_stop_time
    '2021-01-26 01:00:00',
    2
),
(
    3,  -- id
    1,  -- segment_id
    'recently failed campaign',
    'Driver',
    'trend',
    True,  -- discount
    'SEGMENT_ERROR',
    True,  -- is_regular
    True,  -- is_active
    '2021-01-01T12:00:00',  -- regular_start_time
    '2021-12-31T12:00:00',  -- regular_stop_time
    '2021-01-26 01:00:00',
    3
),
(
    4,  -- id
    1,  -- segment_id
    'oneshot campaign',
    'Driver',
    'trend',
    True,  -- discount
    'SEGMENT_ERROR',
    False,  -- is_regular
    True,  -- is_active
    null,  -- regular_start_time
    null,  -- regular_stop_time
    '2021-01-26 01:00:00',
    4
),
(
    5,  -- id
    1,  -- segment_id
    'inactive campaign',
    'Driver',
    'trend',
    True,  -- discount
    'SEGMENT_ERROR',
    True,  -- is_regular
    False,  -- is_active
    '2021-01-01T12:00:00',  -- regular_start_time
    '2021-12-31T12:00:00',  -- regular_stop_time
    '2021-01-26 01:00:00',
    5
),
(
    6,  -- id
    1,  -- segment_id
    'empty segment',
    'Driver',
    'trend',
    True,  -- discount
    'SEGMENT_EMPTY',
    True,  -- is_regular
    True,  -- is_active
    '2021-01-01T12:00:00',  -- regular_start_time
    '2021-12-31T12:00:00',  -- regular_stop_time
    '2021-01-26 01:00:00',
    6
);


INSERT INTO crm_admin.schedule
(
    id,
    campaign_id,
    scheduled_for
)
VALUES
(
    2,  -- id
    2,  -- campaign_id
    '2021-01-31 12:00:00'
),
(
    3,  -- id
    3,  -- campaign_id
    '2021-02-01 15:00:00'
),
(
    4,  -- id
    5,  -- campaign_id
    '2021-01-31 12:00:00'
);
