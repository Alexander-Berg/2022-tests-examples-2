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
    'test2_yql_shred_link',
    'test2_yt_table',
    ('{
        "size": 1000,
        "distribution": [
            {
                "city": "Уфа",
                "locales": [
                    { "name": "RU", "value": 500 },
                    { "name": "CZ", "value": 100 }
                ]
            },
            {
                "city": "Казань",
                "locales": [
                    { "name": "RU", "value": 300 },
                    { "name": "CZ", "value": 100 }
                ]
            }
        ]
    }')::jsonb,
    'Filter',
    10,
    '2019-11-20 01:00:00'
),
(
    'test3_yql_shred_link',
    'test3_yt_table',
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
    22.2,
    '2019-11-20 01:00:00'
),
(
    'test4_yql_shred_link',
    'test4_yt_table',
    ('{
        "size": 1000,
        "distribution": [
            {
                "city": "Уфа",
                "locales": [
                    { "name": "RU", "value": 500 },
                    { "name": "CZ", "value": 100 }
                ]
            },
            {
                "city": "Казань",
                "locales": [
                    { "name": "RU", "value": 300 },
                    { "name": "CZ", "value": 100 }
                ]
            }
        ]
    }')::jsonb,
    'Filter',
    33.3,
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
    ('{"channel": "PUSH", "content": "push text", "name": "share_group_1", "share": 20, "send_at": "2019-11-20T04:00:00+03:00"}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    1,
    ('{"channel": "FS", "content": "banner_id", "name": "share_group_2", "share": 10, "send_at": "2019-11-20T04:00:00+03:00"}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    2,
    ('{"channel": "PUSH", "cities": ["Москва", "Орел"], "content": "push text", "limit": 1000, "locales": ["RU"], "name": "filter_group_1", "state": "SENT"}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    2,
    ('{"channel": "FS", "cities": ["Минск", "Могилев", "Орша"], "content": "banner_id", "limit": 500, "locales": ["RU", "BY"], "name": "filter_group_2", "state": "SENT"}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    2,
    ('{"channel": "PUSH", "cities": ["Сызрань", "Рязань"], "content": "push text", "limit": 200, "locales": ["US"], "name": "filter_group_3", "state": "SENT"}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
);

INSERT INTO crm_admin.campaign
(
    name,
    entity_type,
    trend,
    kind,
    discount,
    state,
    owner_name,
    ticket,
    ticket_status,
    created_at,
    updated_at
)
VALUES
(
    'Первая кампания',
    'User',
    'Направление или тип первой кампании',
    'Тип или подтип первой кампании',
    True,
    'NEW',
    'user1',
    'Тикет1',
    'Открыт',
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
),
(
    'Вторая кампания',
    'User',
    'Направление или тип второй кампании',
    'Тип или подтип второй кампании',
    True,
    'READY',
    'user2',
    'Тикет2',
    'Закрыт',
    '2019-03-21 01:00:00',
    '2019-03-21 01:00:00'
),
(
    'Третья кампания',
    'User',
    'Направление или тип третьей кампании',
    'Тип или подтип третьей кампании',
    True,
    'SEGMENT_PREPROCESSING',
    'user3',
    'Тикет3',
    'Решен',
    '2019-03-22 01:00:00',
    '2019-03-22 01:00:00'
),
(
    'Четвертая кампания',
    'User',
    'Направление или тип четвертой кампании',
    'Тип или подтип четвертой кампании',
    True,
    'GROUPS_PRECALCULATING',
    'user4',
    'Тикет4',
    'Открыт',
    '2019-03-23 01:00:00',
    '2019-03-23 01:00:00'
),
(
    'Пятая кампания',
    'User',
    'Направление или тип пятой кампании',
    'Тип или подтип пятой кампании',
    True,
    'PREPARING_VERIFY_PROCESSING',
    'user5',
    'Тикет5',
    'Открыт',
    '2019-03-24 01:00:00',
    '2019-03-24 01:00:00'
),
(
    '6я кампания',
    'User',
    'Направление или тип пятой кампании',
    'Тип или подтип пятой кампании',
    True,
    'SEGMENT_CALCULATING',
    'user5',
    'Тикет5',
    'Открыт',
    '2019-03-24 01:00:00',
    '2019-03-24 01:00:00'
);
