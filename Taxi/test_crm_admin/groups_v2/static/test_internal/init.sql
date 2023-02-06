INSERT INTO crm_admin.segment
(
    yql_shared_url,
    yt_table,
    aggregate_info,
    mode,
    control,
    created_at
)
VALUES
(
    'segment#1 shared link',
    'home/taxi-crm/robot-crm-admin/cmp_1_seg',
    ('{
        "size": 2000,
        "distribution": [
            {
                "city": "Moscow",
                "locales": [
                    { "name": "ru", "value": 1000 },
                    { "name": "en", "value": 500 }
                ]
            },
            {
                "city": "Saint Petersburg",
                "locales": [
                    { "name": "ru", "value": 500 },
                    { "name": "en", "value": 1000 }
                ]
            }
        ]
    }')::jsonb,
    'Share',
    20,
    '2020-06-09 01:00:00'
),
(
    'segment#2 shared link',
    'home/taxi-crm/robot-crm-admin/cmp_2_seg',
    ('{
        "size": 2000,
        "distribution": [
            {
                "city": "Moscow",
                "locales": [
                    { "name": "ru", "value": 1000 },
                    { "name": "en", "value": 500 }
                ]
            },
            {
                "city": "Saint Petersburg",
                "locales": [
                    { "name": "ru", "value": 500 },
                    { "name": "en", "value": 1000 }
                ]
            }
        ]
    }')::jsonb,
    'Filter',
    20,
    '2020-06-09 01:00:00'
);


INSERT INTO crm_admin.creative
(
    name,
    params,
    created_at,
    updated_at
)
VALUES
(
    'creative 1',
    ('{"channel_name": "user_push", "content": "push text"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    'creative 2',
    ('{"channel_name": "user_push", "content": "push text"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    'creative 3',
    ('{"channel_name": "user_push", "content": "push text"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    'creative 4',
    ('{"channel_name": "user_push", "content": "push text"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    'creative 5',
    ('{"channel_name": "user_push", "content": "push text"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
);


INSERT INTO crm_admin.group_v2
(
    creative_id,
    segment_id,
    name,
    type,
    params,
    send_at,
    created_at,
    updated_at,
    yql_shared_url
)
VALUES
(
    1,
    1,
    'share_group_1',
    'SHARE',
    ('{"channel": "PUSH", "content": "push text", "share": 20}')::jsonb,
    '2019-11-20T01:00:00',
    '2020-06-09 01:00:00',
    '2020-06-09 01:00:00',
    'yql link'
),
(
    2,
    1,
    'share_group_2',
    'SHARE',
    ('{"channel": "PUSH", "content": "push text", "share": 10}')::jsonb,
    '2019-11-20T01:00:00',
    '2020-06-09 01:00:00',
    '2020-06-09 01:00:00',
    'yql link'
),
(
    3,
    2,
    'filter_group_1',
    'FILTER',
    ('{"channel": "PUSH", "cities": ["Moscow"], "content": "push text", "limit": 100, "locales": []}')::jsonb,
    null,
    '2020-06-09 01:00:00',
    '2020-06-09 01:00:00',
    'yql link'
),
(
    4,
    2,
    'filter_group_2',
    'FILTER',
    ('{"channel": "PUSH", "cities": ["Moscow", "Saint Petersburg"], "content": "push text", "limit": 100, "locales": ["ru"]}')::jsonb,
    null,
    '2020-06-09 01:00:00',
    '2020-06-09 01:00:00',
    'yql link'
),
(
    5,
    2,
    'filter_group_3',
    'FILTER',
    ('{"channel": "PUSH", "cities": ["Moscow", "Saint Petersburg"], "content": "push text", "limit": 100, "locales": ["en"]}')::jsonb,
    null,
    '2020-06-09 01:00:00',
    '2020-06-09 01:00:00',
    'yql link'
);


INSERT INTO crm_admin.campaign
(
    name,
    segment_id,
    entity_type,
    trend,
    kind,
    discount,
    state,
    owner_name,
    global_control,
    ticket,
    created_at,
    is_active,
    test_users,
    com_politic,
    efficiency,
    tasks,
    planned_start_date
)
VALUES
(
    'campaing #1',
    1,
    'User',
    'campaign #1 trend',
    'campaign #1 kind',
    True,
    'GROUPS_READY',
    'user1',
    True,
    'ticket #1',
    '2020-04-01 01:00:00',
    True,
    '{}',
    False,
    False,
    '{}',
    CURRENT_DATE
),
(
    'campaing #2',
    2,
    'User',
    'campaign #2 trend',
    'campaign #2 kind',
    True,
    'GROUPS_READY',
    'user2',
    False,
    'ticket #2',
    '2020-04-01 01:00:00',
    True,
    '{}',
    False,
    False,
    '{}',
    CURRENT_DATE
),
(
    'campaing #3',
    Null,
    'User',
    'campaign #3 trend',
    'campaign #3 kind',
    True,
    'NEW',
    'user2',
    False,
    'ticket #3',
    '2020-04-01 01:00:00',
    False,
    '{}',
    False,
    False,
    '{}',
    CURRENT_DATE
);


INSERT INTO crm_admin.campaign_creative_connection
(
    campaign_id,
    creative_id,
    created_at
) VALUES
(1, 1, NOW()),
(1, 2, NOW()),
(2, 3, NOW()),
(2, 4, NOW()),
(2, 5, NOW())
;
