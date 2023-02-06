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
),
(
     8,  -- id
    'yql_shared_url',
    'yt_table',
    'Share',
    20,
    '2021-01-27 01:00:00'
),
(
     9,  -- id
    'yql_shared_url',
    'yt_table',
    'Share',
    20,
    '2021-01-27 01:00:00'
),
(
     10,  -- id
    'yql_shared_url',
    'yt_table',
    'Share',
    20,
    '2021-01-27 01:00:00'
),
(
     11,  -- id
    'yql_shared_url',
    'yt_table',
    'Share',
    20,
    '2021-01-27 01:00:00'
),
(
     12,  -- id
    'yql_shared_url',
    'yt_table',
    'Share',
    20,
    '2021-01-27 01:00:00'
),
(
     13,  -- id
    'yql_shared_url',
    'yt_table',
    'Share',
    20,
    '2021-01-27 01:00:00'
),
(
     14,  -- id
    'yql_shared_url',
    'yt_table',
    'Share',
    20,
    '2021-01-27 01:00:00'
),
(
     16,  -- id
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
    ('{"name": "group1", "share": 10, "state": "SCHEDULED"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    2,  -- id
    2,  -- segment_id
    ('{"name": "group1", "share": 10, "state": "TESTING"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    3,  -- id
    3,  -- segment_id
    ('{"name": "group1", "share": 10, "state": "NEW"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    4,  -- id
    4,  -- segment_id
    ('{"name": "group1", "share": 10, "state": "NEW"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    5,  -- id
    5,  -- segment_id
    ('{"name": "group1", "share": 10, "state": "NEW"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    6,  -- id
    6,  -- segment_id
    ('{"name": "group1", "share": 10, "state": "SENDING"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    7,  -- id
    7,  -- segment_id
    ('{"name": "group1", "share": 10, "state": "SCHEDULED"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    8,  -- id
    8,  -- segment_id
    ('{"name": "group1", "share": 10, "state": "EFFICIENCY_ANALYSIS", ' ||
     ' "efficiency_date": ["", "2021-01-27"], "efficiency_time": ["", "01:00"], ' ||
     '"computed": {"total": 100}}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    9,  -- id
    9,  -- segment_id
    ('{"name": "group1", "share": 10, "state": "EFFICIENCY_ANALYSIS", ' ||
     ' "efficiency_date": ["", "2021-01-27"], "efficiency_time": ["", "01:00"], ' ||
     '"computed": {"total": 120}}')::jsonb,
    '2021-03-27 01:00:00',
    '2021-03-27 01:00:00'
),
(
    11,  -- id
    11,  -- segment_id
    ('{"name": "group1", "share": 10, "state": "EFFICIENCY_ANALYSIS", ' ||
     ' "efficiency_date": ["", "2021-01-27"], "efficiency_time": ["", "01:00"], ' ||
     '"computed": {"total": 120}}')::jsonb,
    '2021-03-27 01:00:00',
    '2021-03-27 01:00:00'
),
(
    13,  -- id
    13,  -- segment_id
    ('{"name": "group1", "share": 10, "state": "EFFICIENCY_SCHEDULED", ' ||
     ' "efficiency_date": ["2021-01-27", "2021-01-28"], "efficiency_time": ["00:00", "01:00"], ' ||
     '"computed": {"total": 100}}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    14,  -- id
    14,  -- segment_id
    ('{"name": "group1", "share": 10, "state": "EFFICIENCY_SCHEDULED", ' ||
     ' "efficiency_date": ["2021-01-27", "2021-01-28"], "efficiency_time": ["00:00", "01:00"], ' ||
     '"computed": {"total": 120}}')::jsonb,
    '2021-03-27 01:00:00',
    '2021-03-27 01:00:00'
),
(
    15,  -- id
    14,  -- segment_id
    ('{"name": "group1", "share": 10, "state": "EFFICIENCY_ANALYSIS", ' ||
     ' "efficiency_date": ["2021-01-27", "2021-01-28"], "efficiency_time": ["00:00", "01:00"], ' ||
     '"computed": {"total": 120}}')::jsonb,
    '2021-03-27 01:00:00',
    '2021-03-27 01:00:00'
),
(
    16,  -- id
    16,  -- segment_id
    ('{"name": "group1", "share": 10, "state": "TESTING"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
);

INSERT INTO crm_admin.group
(
    id,
    segment_id,
    params,
    sending_stats,
    created_at,
    updated_at
)
VALUES
(
    10,  -- id
    10,  -- segment_id
    ('{"name": "group1", "share": 10, "state": "EFFICIENCY_ANALYSIS", ' ||
     ' "efficiency_date": ["", "2021-01-27"], "efficiency_time": ["", "01:00"], ' ||
     '"computed": {"total": 120}}')::jsonb,
    ('{}')::jsonb,
    '2021-03-27 01:00:00',
    '2021-03-27 02:00:00'
),
(
    12,  -- id
    12,  -- segment_id
    ('{"name": "group1", "share": 10, "state": "EFFICIENCY_ANALYSIS", ' ||
     ' "efficiency_date": ["", "2021-01-27"], "efficiency_time": ["", "01:00"], ' ||
     '"computed": {"total": 120}}')::jsonb,
    ('{}')::jsonb,
    '2021-03-27 01:00:00',
    '2021-03-27 02:00:00'
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
    efficiency
)
VALUES
(
    1,  -- id
    1,  -- segment_id
    'send production',
    'User',
    'trend',
    True,  -- discount
    'CAMPAIGN_APPROVED',
    False,  -- is_regular
    False,  -- is_active
    '2021-01-26 01:00:00',
    False
),
(
    2,  -- id
    2,  -- segment_id
    'send verify',
    'User',
    'trend',
    True,  -- discount
    'CAMPAIGN_APPROVED',
    False,  -- is_regular
    False,  -- is_active
    '2021-01-26 01:00:00',
    False
),
(
    3,  -- id
    3,  -- segment_id
    'in process',
    'User',
    'trend',
    True,  -- discount
    'SENDING_PROCESSING',
    False,  -- is_regular
    False,  -- is_active
    '2021-01-26 01:00:00',
    False
),
(
    4,  -- id
    4,  -- segment_id
    'regular',
    'User',
    'trend',
    True,  -- discount
    'GROUPS_FINISHED',
    True,  -- is_regular
    True,  -- is_active
    '2021-01-26 01:00:00',
    False
),
(
    5,  -- id
    5,  -- segment_id
    'regular inactive',
    'User',
    'trend',
    True,  -- discount
    'GROUPS_FINISHED',
    True,  -- is_regular
    False,  -- is_active
    '2021-01-26 01:00:00',
    False
),
(
    6,  -- id
    6,  -- segment_id
    'inactive yet being sending',
    'User',
    'trend',
    True,  -- discount
    'SENDING_PROCESSING',
    True,  -- is_regular
    False,  -- is_active
    '2021-01-26 01:00:00',
    False
),
(
    7,  -- id
    7,  -- segment_id
    'regular',
    'User',
    'trend',
    True,  -- discount
    'SENDING_PROCESSING',
    True,  -- is_regular
    True,  -- is_active
    '2021-01-26 01:00:00',
    False
),
(
    8,  -- id
    8,  -- segment_id
    'regular',
    'User',
    'trend',
    True,  -- discount
    'SENDING_PROCESSING',
    False,  -- is_regular
    False,  -- is_active
    '2021-01-26 01:00:00',
    True
),
(
    9,  -- id
    9,  -- segment_id
    'regular',
    'User',
    'trend',
    True,  -- discount
    'SENDING_PROCESSING',
    False,  -- is_regular
    False,  -- is_active
    '2021-01-26 01:00:00',
    True
),
(
    10,  -- id
    10,  -- segment_id
    'regular',
    'User',
    'trend',
    True,  -- discount
    'SENDING_PROCESSING',
    False,  -- is_regular
    False,  -- is_active
    '2021-01-26 01:00:00',
    False
),
(
    11,  -- id
    11,  -- segment_id
    'regular',
    'User',
    'trend',
    True,  -- discount
    'SENDING_PROCESSING',
    False,  -- is_regular
    False,  -- is_active
    '2021-01-26 01:00:00',
    False
),
(
    12,  -- id
    12,  -- segment_id
    'regular',
    'User',
    'trend',
    True,  -- discount
    'SENDING_PROCESSING',
    False,  -- is_regular
    False,  -- is_active
    '2021-01-26 01:00:00',
    False
),
(
    13,  -- id
    13,  -- segment_id
    'regular',
    'User',
    'trend',
    True,  -- discount
    'SCHEDULED',
    False,  -- is_regular
    False,  -- is_active
    '2021-01-28 01:00:00',
    True
),
(
    14,  -- id
    14,  -- segment_id
    'regular',
    'User',
    'trend',
    True,  -- discount
    'SCHEDULED',
    False,  -- is_regular
    False,  -- is_active
    '2021-01-27 01:00:00',
    True
),
(
    16,  -- id
    16,  -- segment_id
    'regular',
    'User',
    'trend',
    True,  -- discount
    'VERIFY_PROCESSING',
    True,  -- is_regular
    True,  -- is_active
    '2021-01-26 01:00:00',
    False
);


INSERT INTO crm_admin.sending
(
    id,
    campaign_id,
    group_id,
    type,
    state,
    created_at,
    updated_at,
    send_at
)
VALUES
(
    1,  -- id
    1,  -- campaign_id
    1,  -- group_id
    'PRODUCTION',
    'NEW',
    '2021-02-04 01:00:00',
    '2021-02-04 02:00:00',
    '2021-02-04 02:00:00'
),
(
    2,  -- id
    2,  -- campaign_id
    2,  -- group_id
    'VERIFY',
    'NEW',
    '2021-02-04 01:00:00',
    '2021-02-04 02:00:00',
    '2021-02-04 02:00:00'
),
(
    3,  -- id
    3,  -- campaign_id
    3,  -- group_id
    'PRODUCTION',
    'PROCESSING',
    '2021-02-04 01:00:00',
    '2021-02-04 02:00:00',
    '2021-02-04 02:00:00'
),
(
    4,  -- id
    4,  -- campaign_id
    4,  -- group_id
    'PRODUCTION',
    'NEW',
    '2021-02-04 01:00:00',
    '2021-02-04 02:00:00',
    '2021-02-04 02:00:00'
),
(
    5,  -- id
    5,  -- campaign_id
    5,  -- group_id
    'PRODUCTION',
    'NEW',
    '2021-02-04 01:00:00',
    '2021-02-04 02:00:00',
    '2021-02-04 02:00:00'
),
(
    6,  -- id
    6,  -- campaign_id
    6,  -- group_id
    'PRODUCTION',
    'PROCESSING',
    '2021-02-04 01:00:00',
    '2021-02-04 02:00:00',
    '2021-02-04 02:00:00'
),
(
    7,  -- id
    7,  -- campaign_id
    7,  -- group_id
    'PRODUCTION',
    'PROCESSING',
    '2021-02-04 01:00:00',
    '2021-02-04 02:00:00',
    '2021-02-04 02:00:00'
),
(
    8,  -- id
    8,  -- campaign_id
    8,  -- group_id
    'PRODUCTION',
    'PROCESSING',
    '2021-02-04 01:00:00',
    '2021-02-04 02:00:00',
    '2021-02-04 02:00:00'
),
(
    9,  -- id
    9,  -- campaign_id
    9,  -- group_id
    'PRODUCTION',
    'PROCESSING',
    '2021-02-04 01:00:00',
    '2021-02-04 02:00:00',
    '2021-02-04 02:00:00'
),
(
    10,  -- id
    10,  -- campaign_id
    10,  -- group_id
    'PRODUCTION',
    'PROCESSING',
    '2021-02-04 01:00:00',
    '2021-02-04 02:00:00',
    '2021-02-04 02:00:00'
),
(
    11,  -- id
    11,  -- campaign_id
    11,  -- group_id
    'PRODUCTION',
    'FINISHED',
    '2021-02-04 01:00:00',
    '2021-02-04 02:00:00',
    '2021-02-04 02:00:00'
),
(
    12,  -- id
    12,  -- campaign_id
    12,  -- group_id
    'PRODUCTION',
    'FINISHED',
    '2021-02-04 01:00:00',
    '2021-02-04 02:00:00',
    '2021-02-04 02:00:00'
),
(
    13,  -- id
    13,  -- campaign_id
    13,  -- group_id
    'PRODUCTION',
    'NEW',
    '2021-02-04 01:00:00',
    '2021-02-04 02:00:00',
    '2021-01-29 02:00:00'
),
(
    14,  -- id
    14,  -- campaign_id
    14,  -- group_id
    'PRODUCTION',
    'NEW',
    '2021-02-04 01:00:00',
    '2021-02-04 02:00:00',
    '2021-01-28 00:00:00'
),
(
    16,  -- id
    16,  -- campaign_id
    16,  -- group_id
    'VERIFY',
    'PROCESSING',
    '2021-02-04 01:00:00',
    '2021-02-04 02:00:00',
    '2021-01-28 00:00:00'
);

INSERT INTO crm_admin.schedule
(
    id,
    campaign_id,
    scheduled_for,
    started_at,
    sending_stats
)
VALUES
(
    1,  -- id
    6,  -- campaign_id
    '2021-01-26 11:00:00',
    '2021-01-26 11:10:00',
    '{}'
);
