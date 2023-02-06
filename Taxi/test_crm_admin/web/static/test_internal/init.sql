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


INSERT INTO crm_admin.group
(
    segment_id,
    params,
    created_at,
    updated_at,
    yql_shared_url
)
VALUES
(
    1,
    ('{"channel": "PUSH", "content": "push text", "name": "share_group_1", "share": 20, "send_at": "2019-11-20T04:00:00+03:00"}')::jsonb,
    '2020-06-09 01:00:00',
    '2020-06-09 01:00:00',
    'yql link'
),
(
    1,
    ('{"channel": "PUSH", "content": "push text", "name": "share_group_2", "share": 10, "send_at": "2019-11-20T04:00:00+03:00"}')::jsonb,
    '2020-06-09 01:00:00',
    '2020-06-09 01:00:00',
    'yql link'
),
(
    2,
    ('{"channel": "PUSH", "cities": ["Moscow"], "content": "push text", "limit": 100, "locales": [], "name": "filter_group_1"}')::jsonb,
    '2020-06-09 01:00:00',
    '2020-06-09 01:00:00',
    'yql link'
),
(
    2,
    ('{"channel": "PUSH", "cities": ["Moscow", "Saint Petersburg"], "content": "push text", "limit": 100, "locales": ["ru"], "name": "filter_group_2"}')::jsonb,
    '2020-06-09 01:00:00',
    '2020-06-09 01:00:00',
    'yql link'
),
(
    2,
    ('{"channel": "PUSH", "cities": ["Moscow", "Saint Petersburg"], "content": "push text", "limit": 100, "locales": ["en"], "name": "filter_group_3"}')::jsonb,
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
