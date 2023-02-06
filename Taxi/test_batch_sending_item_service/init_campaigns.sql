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
    'test1_yql_shred_link',
    'test1_yt_table',
    ('{
        "size": 2000,
        "distribution": [
            {
                "city": "Москва",
                "locales": [
                    { "name": "RU", "value": 1000 },
                    { "name": "CZ", "value": 500 }
                ]
            },
            {
                "city": "Москва",
                "locales": [
                    { "name": "RU", "value": 1000 },
                    { "name": "CZ", "value": 500 }
                ]
            }
        ]
    }')::jsonb,
    'Share',
    20,
    '2019-11-20 01:00:00'
),
(
    'test1_yql_shred_link',
    'test1_yt_table',
    ('{
        "size": 2000,
        "distribution": [
            {
                "city": "Москва",
                "locales": [
                    { "name": "RU", "value": 1000 },
                    { "name": "CZ", "value": 500 }
                ]
            },
            {
                "city": "Москва",
                "locales": [
                    { "name": "RU", "value": 1000 },
                    { "name": "CZ", "value": 500 }
                ]
            }
        ]
    }')::jsonb,
    'Share',
    20,
    '2019-11-20 01:00:00'
),
(
    'test1_yql_shred_link',
    'test1_yt_table',
    ('{
        "size": 2000,
        "distribution": [
            {
                "city": "Москва",
                "locales": [
                    { "name": "RU", "value": 1000 },
                    { "name": "CZ", "value": 500 }
                ]
            },
            {
                "city": "Москва",
                "locales": [
                    { "name": "RU", "value": 1000 },
                    { "name": "CZ", "value": 500 }
                ]
            }
        ]
    }')::jsonb,
    'Share',
    20,
    '2019-11-20 01:00:00'
),
(
    'test1_yql_shred_link',
    'test1_yt_table',
    ('{
        "size": 2000,
        "distribution": [
            {
                "city": "Москва",
                "locales": [
                    { "name": "RU", "value": 1000 },
                    { "name": "CZ", "value": 500 }
                ]
            },
            {
                "city": "Москва",
                "locales": [
                    { "name": "RU", "value": 1000 },
                    { "name": "CZ", "value": 500 }
                ]
            }
        ]
    }')::jsonb,
    'Share',
    20,
    '2019-11-20 01:00:00'
);

INSERT INTO crm_admin.group
(
    segment_id,
    params,
    created_at,
    updated_at
)
VALUES
(
    1,
    ('{"channel": "LEGACYWALL", "feed_id": "1234", "content": "push text", "name": "share_group_1", "share": 20, "send_at": "2019-11-20T04:00:00+03:00"}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    2,
    ('{"channel": "LEGACYWALL", "feed_id": "1234", "content": "push text", "name": "share_group_1", "share": 20, "send_at": "2019-11-20T04:00:00+03:00"}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    3,
    ('{"channel": "LEGACYWALL", "feed_id": "1234", "content": "push text", "name": "share_group_1", "share": 20, "send_at": "2019-11-20T04:00:00+03:00"}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    4,
    ('{"channel": "LEGACYWALL", "feed_id": "1234", "content": "push text", "name": "share_group_1", "share": 20, "send_at": "2019-11-20T04:00:00+03:00"}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
);

INSERT INTO crm_admin.campaign
(
    id,
    name,
    specification,
    entity_type,
    trend,
    kind,
    subkind,
    discount,
    state,
    owner_name,
    settings,
    ticket,
    ticket_status,
    creative,
    test_users,
    segment_id,
    created_at,
    updated_at
)
VALUES
(
    1,
    'name',
    'spec',
    'Driver',
    'trend_1',
    'kind_1',
    'subkind_1',
    True,
    'NEW',
    'user6',
    NULL,
    'Тикет6',
    'Открыт',
    'creative',
    ARRAY ['test1_user1', 'test1_user2'],
    1,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
),
(
    2,
    'name',
    'spec',
    'Driver',
    'trend_2',
    'kind_2',
    'subkind_2',
    True,
    'NEW',
    'user6',
    NULL,
    'Тикет6',
    'Открыт',
    'creative',
    ARRAY ['test1_user1', 'test1_user2'],
    2,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
),
(
    3,
    'name',
    'spec',
    'Driver',
    'trend_2',
    'kind_3',
    'subkind_3',
    True,
    'NEW',
    'user6',
    NULL,
    'Тикет6',
    'Открыт',
    'creative',
    ARRAY ['test1_user1', 'test1_user2'],
    3,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
),
(
    4,
    'name',
    'spec',
    'Driver',
    'trend_2',
    'kind_3',
    'subkind_4',
    True,
    'NEW',
    'user6',
    NULL,
    'Тикет6',
    'Открыт',
    'creative',
    ARRAY ['test1_user1', 'test1_user2'],
    4,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
);
