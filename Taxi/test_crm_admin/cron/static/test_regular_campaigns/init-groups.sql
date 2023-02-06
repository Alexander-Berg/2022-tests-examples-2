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
    'campaing #1',
    'User',
    'trend',
    True,  -- discount
    'SEGMENT_FINISHED',
    True,  -- is_regular
    True,  -- is_active
    '2021-01-01 01:00:00',  -- regular_start_time
    '2021-12-31 01:00:00',  -- regular_stop_time
    '2021-01-26 01:00:00'
),
(
    2,  -- id
    'campaing #2',
    'Driver',
    'trend',
    True,  -- discount
    'READY',
    True,  -- is_regular
    True,  -- is_active
    '2021-01-01 01:00:00',  -- regular_start_time
    '2021-12-31 01:00:00',  -- regular_stop_time
    '2021-01-26 01:00:00'
),
(
    3,  -- id
    'campaing #3',
    'User',
    'trend',
    True,  -- discount
    'GROUPS_READY',
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
    started_at
)
VALUES
(
    1,  -- id
    1,  -- campaign_id
    '2021-01-26 12:00:00',
    '2021-01-26 12:10:00'
),
(
    3,  -- id
    2,  -- campaign_id
    '2021-01-26 12:00:00',
    '2021-01-26 12:10:00'
),
(
    4,  -- id
    3,  -- campaign_id
    '2021-01-26 12:00:00',
    '2021-01-26 12:10:00'
);
