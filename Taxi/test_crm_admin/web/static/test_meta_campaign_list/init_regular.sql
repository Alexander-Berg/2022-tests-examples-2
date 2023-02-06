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
    params,
    actual_date_params
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
    '{}',
    '{"using_timezone_for_date": true, "using_timezone_for_daytime": true}'
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
    regular_start_time,
    regular_stop_time
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
    True,  -- is_regular
    False,  -- is_active
    '2021-01-26 01:00:00',
    '2021-03-27 02:00:00',
    False,
    '2021-03-27 07:00:00',
    '2021-03-30 20:00:00'
);
