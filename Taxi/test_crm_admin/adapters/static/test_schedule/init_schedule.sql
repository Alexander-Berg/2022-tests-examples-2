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
    'yt_table',
    'Share',
    20,
    '2021-01-01 01:00:00'
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
    created_at,
    root_id
)
VALUES
(
    1,  -- id
    1,  -- segmet_id
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
    '2021-01-26 01:00:00',
    1
),
(
    2,  -- id
    1,  -- segmet_id
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
    '2021-01-26 01:00:00',
    2
),
(
    3,  -- id
    1,  -- segmet_id
    'expired campaign',
    'User',
    'trend',
    True,  -- discount
    'SCHEDULED',
    True,  -- is_regular
    True,  -- is_active
    '1 12 * * *',  -- schedule
    '2021-01-01 01:00:00',  -- regular_start_time
    '2021-03-25 01:00:00',  -- regular_stop_time
    '2021-01-26 01:00:00',
    3
),
(
    4,  -- id
    1,  -- segmet_id
    'expired sending campaign',
    'User',
    'trend',
    True,  -- discount
    'SENDING_PROCESSING',
    True,  -- is_regular
    True,  -- is_active
    '1 12 * * *',  -- schedule
    '2021-01-01 01:00:00',  -- regular_start_time
    '2021-03-25 01:00:00',  -- regular_stop_time
    '2021-01-26 01:00:00',
    4
),
(
    5,  -- id
    1,  -- segmet_id
    'finished campaign',
    'User',
    'trend',
    True,  -- discount
    'COMPLETED',
    True,  -- is_regular
    False,  -- is_active
    '1 12 * * *',  -- schedule
    '2021-01-01 01:00:00',  -- regular_start_time
    '2021-02-01 01:00:00',  -- regular_stop_time
    '2021-01-26 01:00:00',
    5
),
(
    6,  -- id
    1,  -- segmet_id
    'pending and started campaign',
    'User',
    'trend',
    True,  -- discount
    'SCHEDULED',
    True,  -- is_regular
    True,  -- is_active
    '1 12 * * *',  -- schedule
    '2021-01-01 01:00:00',  -- regular_start_time
    '2021-12-31 01:00:00',  -- regular_stop_time
    '2021-01-26 01:00:00',
    6
),
(
    7,  -- id
    1,  -- segmet_id
    'pending but not yet started campaign',
    'User',
    'trend',
    True,  -- discount
    'SCHEDULED',
    True,  -- is_regular
    True,  -- is_active
    '1 12 * * *',  -- schedule
    '2021-01-01 01:00:00',  -- regular_start_time
    '2021-12-31 01:00:00',  -- regular_stop_time
    '2021-01-26 01:00:00',
    7
),
(
    8,  -- id
    1,  -- segmet_id
    'fresh regular campaign',
    'User',
    'trend',
    True,  -- discount
    'SCHEDULED',
    True,  -- is_regular
    True,  -- is_active
    '1 12 * * *',  -- schedule
    '2021-01-01 01:00:00',  -- regular_start_time
    '2021-12-31 01:00:00',  -- regular_stop_time
    '2021-01-26 01:00:00',
    8
),
(
    9,  -- id
    1,  -- segmet_id
    'pending and not started',
    'User',
    'trend',
    True,  -- discount
    'SCHEDULED',
    True,  -- is_regular
    True,  -- is_active
    '1 12 * * *',  -- schedule
    '2021-01-01 01:00:00',  -- regular_start_time
    '2021-12-31 01:00:00',  -- regular_stop_time
    '2021-01-26 01:00:00',
    9
),
(
    10,  -- id
    1,  -- segmet_id
    'pending and started',
    'User',
    'trend',
    True,  -- discount
    'SCHEDULED',
    True,  -- is_regular
    True,  -- is_active
    '1 12 * * *',  -- schedule
    '2021-01-01 01:00:00',  -- regular_start_time
    '2021-12-31 01:00:00',  -- regular_stop_time
    '2021-01-26 01:00:00',
    10
);


INSERT INTO crm_admin.schedule
(
    id,
    campaign_id,
    scheduled_for,
    started_at,
    finished_at,
    sending_stats
)
VALUES
(
    1,  -- id
    1,  -- campaign_id
    '2021-01-26 11:00:00',
    '2021-01-26 11:10:00',
    '2021-01-26 11:30:00',
    '{}'
),
(
    2,  -- id
    1,  -- campaign_id
    '2021-01-26 12:00:00',
    '2021-01-26 12:10:00',
    '2021-01-26 12:30:00',
    '{}'
),
(
    3,  -- id
    1,  -- campaign_id
    '2021-01-26 13:00:00',
    '2021-01-26 13:10:00',
    '2021-01-26 13:30:00',
    '{}'
),
(
    4,  -- id
    1,  -- campaign_id
    '2021-01-26 14:00:00',
    '2021-01-26 14:10:00',
    '2021-01-26 14:30:00',
    '{}'
),
(
    5,  -- id
    1,  -- campaign_id
    '2021-01-26 15:00:00',
    '2021-01-26 15:10:00',
    '2021-01-26 15:30:00',
    '{}'
),
(
    6,  -- id
    2,  -- campaign_id
    '2021-01-26 06:00:00',
    '2021-01-26 06:10:00',
    '2021-01-26 06:30:00',
    '{}'
),
(
    7,  -- id
    2,  -- campaign_id
    '2021-01-26 07:00:00',
    '2021-01-26 07:10:00',
    '2021-01-26 07:30:00',
    '{}'
),
(
    8,  -- id
    2,  -- campaign_id
    '2021-01-26 08:00:00',
    '2021-01-26 08:10:00',
    '2021-01-26 08:30:00',
    '{}'
),
(
    9,  -- id
    2,  -- campaign_id
    '2021-01-26 09:00:00',
    '2021-01-26 09:10:00',
    '2021-01-26 09:30:00',
    '{}'
),
(
    10,  -- id
    2,  -- campaign_id
    '2021-01-26 10:00:00',
    '2021-01-26 10:10:00',
    '2021-01-26 10:30:00',
    '{}'
),
(
    11,  -- id
    6,  -- campaign_id
    '2021-01-26 10:00:00',  -- scheduled_for
    '2021-01-26 10:10:00',  -- started_at
    null,                   -- finished_at
    null
),
(
    12,  -- id
    7,  -- campaign_id
    '2021-01-26 10:00:00',  -- scheduled_for
    null,                   -- started_at
    null,                   -- finished_at
    null
),
(
    13,  -- id
    9,  -- campaign_id
    '2021-01-26 10:00:00',  -- scheduled_for
    '2021-01-26 10:00:00',  -- started_at
    null,                   -- finished_at
    null
),
(
    14,  -- id
    9,  -- campaign_id
    '2021-01-26 11:00:00',  -- scheduled_for
    null,                   -- started_at
    null,                   -- finished_at
    null
),
(
    15,  -- id
    10,  -- campaign_id
    '2021-01-26 10:00:00',  -- scheduled_for
    null,                   -- started_at
    null,                   -- finished_at
    null
),
(
    16,  -- id
    10,  -- campaign_id
    '2021-01-26 11:00:00',  -- scheduled_for
    '2021-01-26 10:00:00',  -- started_at
    null,                   -- finished_at
    null
);
