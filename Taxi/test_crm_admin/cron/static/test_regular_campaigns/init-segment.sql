INSERT INTO crm_admin.campaign
(
    id,
    name,
    entity_type,
    trend,
    discount,
    state,
    is_regular,
    is_active,
    regular_start_time,
    regular_stop_time,
    created_at
)
VALUES
(
    1,  -- id
    'active user campaign',
    'User',
    'trend',
    True,  -- discount
    'SCHEDULED',
    True,  -- is_regular
    True,  -- is_active
    '2021-01-01 01:00:00',  -- regular_start_time
    '2021-12-31 01:00:00',  -- regular_stop_time
    '2021-01-26 01:00:00'
),
(
    2,  -- id
    'active user campaign',
    'Driver',
    'trend',
    True,  -- discount
    'SCHEDULED',
    True,  -- is_regular
    True,  -- is_active
    '2021-01-01 01:00:00',  -- regular_start_time
    '2021-12-31 01:00:00',  -- regular_stop_time
    '2021-01-26 01:00:00'
),
(
    3,  -- id
    'not queued',
    'Driver',
    'trend',
    True,  -- discount
    'SCHEDULED',
    True,  -- is_regular
    True,  -- is_active
    '2021-01-01 01:00:00',  -- regular_start_time
    '2021-12-31 01:00:00',  -- regular_stop_time
    '2021-01-26 01:00:00'
),
(
    4,  -- id
    'inactive',
    'Driver',
    'trend',
    True,  -- discount
    'SCHEDULED',
    True,  -- is_regular
    False,  -- is_active
    '2021-01-01 01:00:00',  -- regular_start_time
    '2021-12-31 01:00:00',  -- regular_stop_time
    '2021-01-26 01:00:00'
),
(
    5,  -- id
    'active user campaign',
    'User',
    'trend',
    True,  -- discount
    'SCHEDULED',
    True,  -- is_regular
    True,  -- is_active
    '2021-01-01 01:00:00',  -- regular_start_time
    '2021-01-25 01:00:00',  -- regular_stop_time
    '2021-01-26 01:00:00'
);


INSERT INTO crm_admin.schedule
(
    id,
    campaign_id,
    scheduled_for,
    started_at,
    finished_at
)
VALUES
(
    1,  -- id
    1,  -- campaign_id
    '2021-01-26 12:00:00',
    '2021-01-26 12:10:00',
    '2021-01-26 12:30:00'
),
(
    2,  -- id
    1,  -- campaign_id
    '2021-01-26 13:00:00',
    Null,
    Null
),
(
    3,  -- id
    2,  -- campaign_id
    '2021-01-26 12:00:00',
    '2021-01-26 12:10:00',
    '2021-01-26 12:30:00'
),
(
    4,  -- id
    2,  -- campaign_id
    '2021-01-26 12:20:00',
    Null,
    Null
),
(
    5,  -- id
    2,  -- campaign_id
    '2021-01-26 12:10:00',
    Null,
    Null
),
(
    6,  -- id
    3,  -- campaign_id
    '2021-01-26 12:10:00',
    '2021-01-26 12:10:00',
    '2021-01-26 12:30:00'
),
(
    7,  -- id
    4,  -- campaign_id
    '2021-01-26 12:10:00',
    Null,
    Null
),
(
    8,  -- id
    5,  -- campaign_id
    '2021-01-26 12:00:00',
    '2021-01-26 12:10:00',
    '2021-01-26 12:30:00'
),
(
    9,  -- id
    5,  -- campaign_id
    '2021-01-26 13:00:00',
    Null,
    Null
);
