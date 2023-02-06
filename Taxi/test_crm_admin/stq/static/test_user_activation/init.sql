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
    '2021-03-04 01:00:00'
),
(
    2,  -- id
    'yql_shared_url',
    'yt_table',
    'Share',
    20,
    '2021-03-04 01:00:00'
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
    ('{"name": "group1", "share": 10, "state": "NEW"}')::jsonb,
    '2021-03-04 01:00:00',
    '2021-03-04 01:00:00'
),
(
    2,  -- id
    2,  -- segment_id
    ('{"name": "group1", "share": 10, "state": "NEW"}')::jsonb,
    '2021-03-04 01:00:00',
    '2021-03-04 01:00:00'
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
    created_at
)
VALUES
(
    1,  -- id
    1,  -- segment_id
    'user campaign',
    'User',
    'trend',
    True,
    'CANCELED',
    '2021-03-04 01:00:00'
),
(
    2,  -- id
    2,  -- segment_id
    'user campaign',
    'zUser',
    'trend',
    True,
    'CANCELED',
    '2021-03-04 01:00:00'
);


INSERT INTO crm_admin.operations(
    id,
    campaign_id,
    operation_name,
    submission_id,
    operation_type,
    status,
    started_at
)
VALUES
(
    1,  -- id
    null,  -- campaign_id
    'user_activation',
    null, -- submission_id
    null, -- operation_type
    null, -- status
    '2021-03-04 01:00:00'
);
