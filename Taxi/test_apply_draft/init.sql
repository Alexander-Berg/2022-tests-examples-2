INSERT INTO crm_admin.segment
(
    id,
    yql_shared_url,
    yt_table,
    aggregate_info,
    mode,
    control,
    created_at
)
VALUES
(
    1,
    'segment1_yql_shred_link',
    'segment1_yt_table',
    ('{}')::jsonb,
    'Share',
    20,
    '2019-11-20 01:00:00'
),
(
    2,
    'segment2_yql_shred_link',
    'segment2_yt_table',
    ('{}')::jsonb,
    'Share',
    20,
    '2019-11-20 01:00:00'
),
(
    3,
    'segment3_yql_shred_link',
    'segment3_yt_table',
    ('{}')::jsonb,
    'Share',
    20,
    '2019-11-20 01:00:00'
),
(
    4,
    'segment4_yql_shred_link',
    'segment4_yt_table',
    ('{}')::jsonb,
    'Share',
    20,
    '2019-11-20 01:00:00'
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
    salt,
    created_at,
    root_id,
    parent_id,
    child_id,
    version_state
)
VALUES
(
    1,
    1,
    'name',
    'User',
    'trend',
    True,
    'SCHEDULED',
    true,
    true,
    'salt',
    '2021-03-12 01:00:00',
    1,
    null,
    2,
    'ACTUAL'
),
(
    2,
    2,
    'name',
    'User',
    'trend',
    True,
    'CAMPAIGN_APPROVED',
    true,
    false,
    'salt',
    '2021-03-12 01:00:00',
    1,
    1,
    null,
    'DRAFT'
),
(
    3,
    3,
    'name',
    'User',
    'trend',
    True,
    'SCHEDULED',
    true,
    true,
    'salt',
    '2021-03-12 01:00:00',
    3,
    null,
    4,
    'ACTUAL'
),
(
    4,
    4,
    'name',
    'User',
    'trend',
    True,
    'GROUPS_FINISHED',
    true,
    true,
    'salt',
    '2021-03-12 01:00:00',
    3,
    3,
    null,
    'DRAFT'
);
