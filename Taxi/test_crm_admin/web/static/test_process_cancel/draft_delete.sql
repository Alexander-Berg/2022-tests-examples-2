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
),
(
    3,
    'yql_shared_url',
    'path/to/segment',
    'Share',
    20,
    '2021-02-03 01:00:00'
),
(
    4,
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
    ticket_status,
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
    'В работе',
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
    'В работе',
    True,  -- is_regular
    True,  -- is_active
    '2021-02-03 01:00:00',
    'DRAFT',
    1,
    1,
    null
),
(
    3,  -- id
    3,  -- segment_id
    'campaign #3',
    'User',
    'trend',
    True,
    'READY',
    'Согласование',
    True,  -- is_regular
    True,  -- is_active
    '2021-02-03 01:00:00',
    'ACTUAL',
    3,
    null,
    4
),
(
    4,  -- id
    4,  -- segment_id
    'campaign #4',
    'User',
    'trend',
    True,
    'READY',
    'Согласование',
    True,  -- is_regular
    True,  -- is_active
    '2021-02-03 01:00:00',
    'DRAFT',
    3,
    3,
    null
)
;
