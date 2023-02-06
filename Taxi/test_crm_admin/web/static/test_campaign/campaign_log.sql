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
    '#1 yql_shared_url',
    '#1 yt_table',
    'Share',
    20,
    '2020-05-16 01:00:00'
),
(  /* no corresponding records in crm_admin.group */
    2,
    '#2 yql_shared_url',
    '#2 yt_table',
    'Share',
    20,
    '2020-05-17 01:00:00'
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
    1,
    1,
    'campaign #1',
    'User',
    '#1 trend',
    True,
    'NEW',
    '2020-05-16 01:00:00'
),
(  /* no corresponding records in crm_admin.{group,nirvana_tast} */
    2,
    2,
    'campaign #2',
    'User',
    '#2 trend',
    True,
    'NEW',
    '2020-05-17 01:00:00'
),
(
    3,
    NULL,  /* segment_id */
    'campaign #3',
    'User',
    '#3 trend',
    True,
    'NEW',
    '2020-05-18 01:00:00'
);


INSERT INTO crm_admin.group
(
    segment_id,
    yql_shared_url,
    params,
    created_at,
    updated_at
)
VALUES
(
    1,
    '#1 yql_shared_url',
    ('{"channel": "PUSH", "content": "push text", "name": "share_group_1", "share": 20}')::jsonb,
    '2020-05-16 01:00:00',
    '2020-05-16 01:00:00'
),
(
    1,
    '#2 yql_shared_url',
    ('{"channel": "PUSH", "content": "push text", "name": "share_group_2", "share": 20}')::jsonb,
    '2020-05-16 01:00:00',
    '2020-05-16 01:00:00'
),
(
    1,
    NULL,  /* yql_shared_url */
    ('{"channel": "PUSH", "content": "push text", "name": "share_group_3", "share": 20}')::jsonb,
    '2020-05-16 01:00:00',
    '2020-05-16 01:00:00'
);


INSERT INTO crm_admin.nirvana_task
(
    campaign_id,
    campaign_task_id,
    description,
    state,
    created_at,
    expires_at
)
VALUES
(
    1,
    1,
    '#1 description',
    'STARTED',
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
);
