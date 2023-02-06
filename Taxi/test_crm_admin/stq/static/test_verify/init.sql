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
    'shared link',
    'path/to/segment_1',
    'Share',
    20,
    '2020-06-09 01:00:00'
),
(
    2,
    'shared link',
    'path/to/segment_2',
    'Share',
    20,
    '2020-06-09 01:00:00'
),
(
    3,
    'shared link',
    'path/to/segment_2',
    'Share',
    20,
    '2020-06-09 01:00:00'
)
;


INSERT INTO crm_admin.creative
(
    id,
    name,
    params,
    created_at,
    updated_at
)
VALUES
(
    1,  -- id
    'creative 1',
    ('{"channel_name": "user_push", "content": "push text"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
)
;


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
    1,
    1,
    ('{"name": "group1", "share": 10, "state": "NEW"}')::jsonb,
    '2020-10-01 01:00:00',
    '2020-10-01 01:00:00'
),
(
    2,
    2,
    ('{"name": "group2", "share": 10, "state": "NEW"}')::jsonb,
    '2020-10-01 01:00:00',
    '2020-10-01 01:00:00'
)
;

INSERT INTO crm_admin.group_v2
(
    id,
    segment_id,
    creative_id,
    state,
    name,
    type,
    params,
    created_at,
    updated_at
)
VALUES
(
    3,
    3,
    1,
    'NEW',
    '1',
    'SHARE',
    ('{"channel": "PUSH", "content": "push text", "name": "share_group_1", "share": 20, "send_at": "2019-11-20T04:00:00+03:00"}')::jsonb,
    '2020-10-01 01:00:00',
    '2020-10-01 01:00:00'
),
(
    4,
    3,
    1,
    'NEW',
    '1',
    'SHARE',
    ('{"channel": "PUSH", "content": "push text", "name": "share_group_1", "share": 20, "send_at": "2019-11-20T04:00:00+03:00"}')::jsonb,
    '2020-10-01 01:00:00',
    '2020-10-01 01:00:00'
),
(
    5,
    3,
    1,
    'NEW',
    '1',
    'SHARE',
    ('{"channel": "PUSH", "content": "push text", "name": "share_group_1", "share": 20, "send_at": "2019-11-20T04:00:00+03:00"}')::jsonb,
    '2020-10-01 01:00:00',
    '2020-10-01 01:00:00'
)
;

INSERT INTO crm_admin.campaign
(
    id,
    segment_id,
    name,
    specification,
    entity_type,
    trend,
    kind,
    discount,
    state,
    owner_name,
    ticket,
    creative,
    test_users,
    settings,
    created_at
)
VALUES
(
    1,
    1,
    'campain #1',
    'specification',
    'User',
    'trend',
    'kind',
    True,
    'GROUPS_FINISHED',
    'user',
    'ticket',
    'creative',
    '{"+7xxxx"}',
    ('[]')::jsonb,
    '2020-03-20 01:00:00'
),
(
    2,
    2,
    'campain #2',
    'specification',
    'Driver',
    'trend',
    'kind',
    True,
    'GROUPS_FINISHED',
    'user',
    'ticket',
    'creative',
    '{"+7xxxx"}',
    ('[]')::jsonb,
    '2020-03-20 01:00:00'
);

INSERT INTO crm_admin.campaign
(
    id,
    segment_id,
    name,
    entity_type,
    trend,
    discount,
    is_regular,
    state,
    created_at
)
VALUES
(
    3,
    2,
    'campaign #3',
    'User',
    'trend',
    False,
    False,
    'SENDING_ERROR',
    '2020-03-20 01:00:00'
),
(
    4,
    2,
    'campaign #4',
    'User',
    'trend',
    False,
    True,
    'STOPPED',
    '2020-03-20 01:00:00'
),
(
    5,
    2,
    'campaign #5',
    'User',
    'trend',
    False,
    False,
    'SENDING_FINISHED',
    '2020-03-20 01:00:00'
),
(
    6,
    3,
    'campaign #6',
    'User',
    'trend',
    False,
    False,
    'GROUPS_FINISHED',
    '2020-03-20 01:00:00'
),
(
    7,
    3,
    'campaign #7',
    'User',
    'trend',
    False,
    False,
    'GROUPS_FINISHED',
    '2020-03-20 01:00:00'
),
(
    8,
    3,
    'campaign #8',
    'User',
    'trend',
    False,
    False,
    'GROUPS_FINISHED',
    '2020-03-20 01:00:00'
)
;
