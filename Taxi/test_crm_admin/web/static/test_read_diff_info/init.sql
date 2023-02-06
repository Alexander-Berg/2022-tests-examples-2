INSERT INTO crm_admin.segment
(
    -- id,
    yql_shared_url,
    yt_table,
    mode,
    control,
    aggregate_info,
    created_at
)
VALUES
(
    -- 1,  -- id
    'yql_shared_url',
    'yt_table',
    'Share',
    20,
    ('{"size": 1000}')::jsonb,
    '2021-02-03 01:00:00'
);

INSERT INTO crm_admin.creative
(
    -- id,
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
    -- 1,  -- id
    'creative 1',
    ('{"channel_name": "user_push", "content": "push message"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00',
    1,
    null,
    3,
    'ARCHIVE'
),
(
    -- 2,  -- id
    'creative 2',
    ('{"channel_name": "driver_wall", "feed_id": "feed_id", "days_count": 10, "time_until": "20:00"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00',
    2,
    null,
    null,
    'ACTUAL'
),
(
    -- 3,  -- id
    'creative 1',
    ('{"channel_name": "user_push", "content": "push message"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00',
    1,
    1,
    null,
    'ACTUAL'
);

INSERT INTO crm_admin.group_v2
(
    -- id,
    creative_id,
    name,
    type,
    state,
    sent,
    segment_id,
    params,
    yql_shared_url,
    created_at,
    updated_at,
    root_id,
    parent_id,
    child_id,
    version_state
)
VALUES
(
    -- 1,  -- id
    2,
    'group_3',
    'SHARE',
    'SENT',
    Null,
    1,  -- segment_id
    ('{"share": 30}')::jsonb,
    'yql_shared_url',
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00',
    1,
    null,
    null,
    'ACTUAL'
);


INSERT INTO crm_admin.campaign
(
    segment_id,
    name,
    entity_type,
    trend,
    discount,
    state,
    settings,
    creative,
    is_regular,
    is_active,
    created_at
)
VALUES
(
    -- 1,  -- id
    1,  -- segment_id
    'wall campaign',
    'Driver',
    'trend',
    True,
    'CAMPAIGN_APPROVED',
    null,
    null,  -- creative
    False,  -- is_regular
    False,  -- is_active
    '2021-02-03 01:00:00'
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
    3,
    '2021-02-03 01:00:00'
),
(
    1,
    2,
    '2021-02-03 01:00:00'
);
