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
),
(
    6,  -- id
    'yql_shared_url',
    'yt_table',
    'Share',
    20,
    '2021-01-27 01:00:00'
),
(
    7,  -- id
    'yql_shared_url',
    'yt_table',
    'Share',
    20,
    '2021-01-27 01:00:00'
);


INSERT INTO crm_admin.creative
(
    id,
    name,
    params,
    created_at,
    updated_at,
    root_id,
    parent_id,
    child_id,
    version_state
)
VALUES
(
    1,
    'creative1',
    '{"channel_name": "driver_sms", "content": "Hello!", "intent": "intent", "sender": "sender"}'::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00',
    1,
    NULL,
    2,
    'ACTUAL'
),
(
    2,
    'creative2',
    '{"channel_name": "driver_sms", "content": "Hello!", "intent": "intent", "sender": "sender"}'::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00',
    1,
    1,
    NULL,
    'DRAFT'
)
;


INSERT INTO crm_admin.group_v2
(
    id,
    name,
    segment_id,
    params,
    created_at,
    updated_at,
    type,
    state,
    version_state,
    root_id,
    parent_id,
    child_id
)
VALUES
(
    1,  -- id
    'group1',
    6,  -- segment_id
    ('{"share": 10}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00',
    'SHARE',
    'NEW',
    'ACTUAL',
    1,
    NULL,
    2
),
(
    2,  -- id
    'group2',
    7,  -- segment_id
    ('{"share": 10}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00',
    'SHARE',
    'NEW',
    'DRAFT',
    1,
    1,
    NULL
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
    version_state,
    root_id,
    parent_id,
    child_id
)
VALUES
(
    1,  -- id
    6,  -- segment_id
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
    'ACTUAL',
    1,
    null,
    9
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
    '2021-01-26 01:00:00',
    'ACTUAL',
    2,
    null,
    null
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
    '2021-01-26 01:00:00',
    'ACTUAL',
    3,
    null,
    null
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
    '2021-01-26 01:00:00',
    'ACTUAL',
    4,
    null,
    null
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
    '2021-01-26 01:00:00',
    'ACTUAL',
    5,
    null,
    null
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
    '2021-01-26 01:00:00',
    'ACTUAL',
    6,
    null,
    null
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
    '2021-01-26 01:00:00',
    'ACTUAL',
    7,
    null,
    null
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
    '2021-01-26 01:00:00',
    'ACTUAL',
    8,
    null,
    null
),
(
    9,  -- id
    7,  -- segment_id
    'Draft to apply',
    'User',
    'trend',
    True,  -- discount
    'APPLYING_DRAFT',
    True,  -- is_regular
    False,  -- is_active
    '1 12 * * *',  -- schedule
    '2021-01-01 01:00:00',  -- regular_start_time
    '2021-12-31 01:00:00',  -- regular_stop_time
    '2021-01-26 01:00:00',
    'DRAFT',
    1,
    1,
    null
),
(
    10,  -- id
    1,  -- segment_id
    'Draft to apply',
    'User',
    'trend',
    True,  -- discount
    'APPLYING_DRAFT',
    True,  -- is_regular
    False,  -- is_active
    '1 12 * * *',  -- schedule
    '2021-01-01 01:00:00',  -- regular_start_time
    '2021-12-31 01:00:00',  -- regular_stop_time
    '2021-01-26 01:00:00',
    'DRAFT',
    10,
    null,
    null
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

INSERT INTO crm_admin.draft_applying
(
    actual_campaign_id,
    draft_campaign_id,
    created_at,
    updated_at
)
VALUES
(
    1,
    9,
    '2021-01-26 12:00:00',
    '2021-01-26 12:00:00'
),
(
    null,
    10,
    '2021-01-26 12:00:00',
    '2021-01-26 12:00:00'
);

INSERT INTO crm_admin.campaign_creative_connection
(
    campaign_id,
    creative_id,
    created_at
)
VALUES
(
    1,
    1,
    '2021-01-26 12:00:00'
),
(
    9,
    2,
    '2021-01-26 12:00:00'
)
;
