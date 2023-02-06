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

INSERT INTO crm_admin.group_v2
(
    id,
    name,
    creative_id,
    segment_id,
    efficiency_date,
    efficiency_time,
    created_at,
    updated_at,
    type,
    params
)
VALUES
(
    1,
    'group1',
    NULL,
    1,
    '{"2021-03-27", "2021-03-30"}',
    '{"07:00", "20:00"}',
    '2021-03-27 01:00:00',
    '2021-03-27 01:00:00',
    'ACTUAL',
    '{}'
),
(
    2,
    'group1',
    NULL,
    2,
    '{"2021-03-27", "2021-03-30"}',
    '{"07:00", "20:00"}',
    '2021-03-27 01:00:00',
    '2021-03-27 01:00:00',
    'ACTUAL',
    '{}'
),
(
    4,
    'group1',
    NULL,
    4,
    '{"2021-03-27", "2021-03-30"}',
    '{"07:00", "20:00"}',
    '2021-03-27 01:00:00',
    '2021-03-27 01:00:00',
    'ACTUAL',
    '{}'
),
(
    5,
    'group1',
    NULL,
    5,
    NULL,
    NULL,
    '2021-03-27 01:00:00',
    '2021-03-27 01:00:00',
    'ACTUAL',
    '{}'
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
    updated_at,
    efficiency,
    efficiency_start_time,
    efficiency_stop_time
)
VALUES
(
    1,  -- id
    1,  -- segment_id
    'name',
    'User',
    'trend',
    True,  -- discount
    'SENDING_PROCESSING',
    False,  -- is_regular
    False,  -- is_active
    '2021-01-26 01:00:00',
    '2021-03-27 02:00:00',
    True,
    '2021-03-27 07:00:00',
    '2021-03-30 21:00:00'
),
(
    2,  -- id
    2,  -- segment_id
    'name',
    'User',
    'trend',
    True,  -- discount
    'SENDING_PROCESSING',
    False,  -- is_regular
    False,  -- is_active
    '2021-01-26 01:00:00',
    '2021-03-27 04:00:00',
    True,
    '2021-03-27 07:00:00',
    '2021-03-30 21:00:00'
),
(
    3,  -- id
    3,  -- segment_id
    'name',
    'User',
    'trend',
    True,  -- discount
    'SENDING_PROCESSING',
    False,  -- is_regular
    False,  -- is_active
    '2021-01-26 01:00:00',
    '2021-03-27 04:00:00',
    True,
    '2021-03-27 07:00:00',
    '2021-03-30 21:00:00'
),
(
    4,  -- id
    4,  -- segment_id
    'name',
    'User',
    'trend',
    True,  -- discount
    'SENDING_PROCESSING',
    False,  -- is_regular
    False,  -- is_active
    '2021-01-26 01:00:00',
    '2021-03-27 04:00:00',
    True,
    '2021-03-27 07:00:00',
    '2021-03-30 21:00:00'
),
(
    5,  -- id
    5,  -- segment_id
    'name',
    'User',
    'trend',
    True,  -- discount
    'SENDING_PROCESSING',
    False,  -- is_regular
    False,  -- is_active
    '2021-01-26 01:00:00',
    '2021-03-27 04:00:00',
    True,
    NULL,
    NULL
);
