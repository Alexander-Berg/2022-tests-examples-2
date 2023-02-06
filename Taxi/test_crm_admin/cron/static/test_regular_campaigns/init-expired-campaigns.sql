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
    created_at
)
VALUES
(
    1,  -- id
    null,  -- segment_id
    'active campaign',
    'User',
    'trend',
    True,  -- discount
    'SCHEDULED',
    True,  -- is_regular
    True,  -- is_active
    '2021-01-01T12:00:00',  -- regular_start_time
    '2021-03-27T12:00:00',  -- regular_stop_time
    '2021-01-26 01:00:00'
),
(
    2,  -- id
    null,  -- segment_id
    'failed expired campaign',
    'Driver',
    'trend',
    True,  -- discount
    'SEGMENT_ERROR',
    True,  -- is_regular
    True,  -- is_active
    '2021-01-01T12:00:00',  -- regular_start_time
    '2021-03-25T12:00:00',  -- regular_stop_time
    '2021-01-26 01:00:00'
),
(
    3,  -- id
    null,  -- segment_id
    'expired idle campaign',
    'Driver',
    'trend',
    True,  -- discount
    'SCHEDULED',
    True,  -- is_regular
    True,  -- is_active
    '2021-01-01T12:00:00',  -- regular_start_time
    '2021-03-25T12:00:00',  -- regular_stop_time
    '2021-01-26 01:00:00'
),
(
    4,  -- id
    null,  -- segment_id
    'sending expired campaign',
    'Driver',
    'trend',
    True,  -- discount
    'SENDING_PROCESSING',
    True,  -- is_regular
    True,  -- is_active
    '2021-01-01T12:00:00',  -- regular_start_time
    '2021-03-25T12:00:00',  -- regular_stop_time
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
    3,  -- campaign_id
    '2021-03-26 12:00:00'
),
(
    2,  -- id
    4,  -- campaign_id
    '2021-03-26 12:00:00'
);
