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
    'path/to/segment',
    'Share',
    20,
    '2021-02-03 01:00:00'
),
(
    2,
    'yql_shared_url',
    'path/to/segment',
    'Share',
    20,
    '2021-02-03 01:00:00'
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
    version_state,
    root_id,
    parent_id,
    child_id
)
VALUES
(
    1,  -- id
    1,  -- segment_id
    'campaign #1',
    'User',
    'trend',
    True,
    'READY',
    True,  -- is_regular
    True,  -- is_active
    '2021-02-03 01:00:00',
    'ACTUAL',
    1,
    null,
    2
),
(
    2,  -- id
    2,  -- segment_id
    'campaign #2',
    'User',
    'trend',
    True,
    'READY',
    True,  -- is_regular
    True,  -- is_active
    '2021-02-03 01:00:00',
    'DRAFT',
    1,
    1,
    null
)
;
