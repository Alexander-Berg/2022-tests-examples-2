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
        ],
        "policy": {
            "push": {
                "size": 1800,
                "blocked_size": 200
            }
        }
    }')::jsonb,
    'Share',
    20,
    '2019-11-20 01:00:00'
),
(
    2,
    'test2_yql_shred_link',
    'test2_yt_table',
    ('{"size": 2000}')::jsonb,
    'Filter',
    10,
    '2019-11-20 01:00:00'
),
(
    3,
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
    4,
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
),
(
    5,
    'test5_yql_shred_link',
    'test5_yt_table',
    ('{"size": 1000, "unique_drivers": 500}')::jsonb,
    'Share',
    10,
    '2019-11-20 01:00:00'
),
(
    6,
    'yql_shred_link',
    'yt_table',
    ('{"size": 1000}')::jsonb,
    'Filter',
    10,
    '2019-11-20 01:00:00'
),
(
    7,
    'yql_shred_link',
    'yt_table',
    ('{"size": 1000}')::jsonb,
    'Filter',
    10,
    '2019-11-20 01:00:00'
),
(
    8,
    'yql_shred_link',
    'yt_table',
    ('{"size": 1000}')::jsonb,
    'Filter',
    10,
    '2019-11-20 01:00:00'
),
(
    9,
    'yql_shred_link',
    'yt_table',
    ('{"size": 1000}')::jsonb,
    'Value',
    10,
    '2019-11-20 01:00:00'
),
(
    10,
    'yql_shred_link',
    'yt_table',
    ('{"size": 0}')::jsonb,
    'Value',
    10,
    '2019-11-20 01:00:00'
);


INSERT INTO crm_admin.group
(
    segment_id,
    params,
    sending_stats,
    yql_shared_url,
    created_at,
    updated_at
)
VALUES
(
    -- id: 1
    1,
    ('{
        "channel": "PUSH",
        "content": "push text",
        "name": "share_group_1",
        "share": 20,
        "send_at": "2019-11-20T04:00:00+03:00",
        "efficiency_time": ["01:00", "02:00"],
        "efficiency_date": ["2021-01-01", "2021-01-02"]
    }')::jsonb,
    null,
    'yql_shared_url',
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 2
    1,
    ('{
        "channel": "FS",
        "content": "banner_id",
        "name": "share_group_2",
        "share": 10,
        "send_at": "2019-11-20T04:00:00+03:00",
        "efficiency_time": ["02:00", "03:00"],
        "efficiency_date": ["2021-01-02", "2021-01-03"]
    }')::jsonb,
    ('{}')::jsonb,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 3
    1,
    ('{
        "channel": "FS",
        "content": "banner_id",
        "name": "share_group_3",
        "computed_share": 10,
        "share": 10,
        "send_at": "2019-11-20T04:00:00+03:00",
        "efficiency_time": ["03:00", "04:00"],
        "efficiency_date": ["2021-01-03", "2021-01-04"]
    }')::jsonb,
    ('{"sent": 100, "failed": 50, "planned": 180, "skipped": 30, "finished_at": "2021-01-20T16:40:00+03:00"}')::jsonb,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 4
    1,
    ('{
        "channel": "FS",
        "content": "banner_id",
        "name": "share_group_4",
        "computed": {"total": 200},
        "share": 10,
        "send_at": "2019-11-20T04:00:00+03:00",
        "efficiency_time": ["04:00", "05:00"],
        "efficiency_date": ["2021-01-04", "2021-01-05"]
    }')::jsonb,
    ('{"sent": 104, "failed": 54, "planned": 192, "skipped": 34, "finished_at": "2021-01-20T16:40:00+03:00"}')::jsonb,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 5
    2,
    ('{
        "channel": "PUSH",
        "cities": ["Москва", "Орел"],
        "content": "push text",
        "limit": 1000,
        "locales": ["RU"],
        "name": "filter_group_1",
        "state": "SENT",
        "efficiency_time": ["05:00", "06:00"],
        "efficiency_date": ["2021-01-05", "2021-01-06"]
    }')::jsonb,
    ('{"sent": 100, "failed": 50, "planned": 180, "skipped": 30, "finished_at": "2021-01-20T16:40:00+03:00"}')::jsonb,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 6
    2,
    ('{
        "channel": "FS",
        "cities": ["Минск", "Могилев", "Орша"],
        "content": "banner_id",
        "limit": 500,
        "locales": ["RU", "BY"],
        "name": "filter_group_2",
        "state": "SENT",
        "efficiency_time": ["06:00", "07:00"],
        "efficiency_date": ["2021-01-06", "2021-01-07"]
    }')::jsonb,
    ('{}')::jsonb,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 7
    2,
    ('{
        "channel": "PUSH",
        "cities": ["Сызрань", "Рязань"],
        "content": "push text",
        "limit": 200,
        "locales": ["US"],
        "name": "filter_group_3",
        "state": "SENT",
        "efficiency_time": ["07:00", "08:00"],
        "efficiency_date": ["2021-01-07", "2021-01-08"]
    }')::jsonb,
    ('{}')::jsonb,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 8
    2,
    ('{
        "channel": "PUSH",
        "cities": ["Сызрань", "Рязань"],
        "content": "push text",
        "limit": 200,
        "locales": ["US"],
        "computed_limit": 210,
        "name": "filter_group_4",
        "state": "SENT",
        "efficiency_time": ["08:00", "09:00"],
        "efficiency_date": ["2021-01-08", "2021-01-09"]
    }')::jsonb,
    ('{}')::jsonb,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 9
    2,
    ('{
        "channel": "PUSH",
        "cities": ["Сызрань", "Рязань"],
        "content": "push text",
        "limit": 200,
        "locales": ["US"],
        "computed": {"total": 210},
        "name": "filter_group_5",
        "state": "SENT",
        "efficiency_time": ["09:00", "10:00"],
        "efficiency_date": ["2021-01-09", "2021-01-10"]
    }')::jsonb,
    ('{}')::jsonb,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 10
    5,
    ('{
        "channel": "PUSH",
        "content": "push text",
        "name": "share_group_1",
        "share": 20,
        "send_at": "2019-11-20T04:00:00+03:00",
        "efficiency_time": ["10:00", "11:00"],
        "efficiency_date": ["2021-01-10", "2021-01-11"]
    }')::jsonb,
    ('{}')::jsonb,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 11
    5,
    ('{
        "channel": "LEGACYWALL",
        "content": "banner_id",
        "name": "share_group_2",
        "computed": {"total": 100},
        "share": 10,
        "send_at": "2019-11-20T04:00:00+03:00",
        "efficiency_time": ["11:00", "12:00"],
        "efficiency_date": ["2021-01-11", "2021-01-12"]
    }')::jsonb,
    ('{}')::jsonb,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 12
    6,
    ('{
        "channel": "FS",
        "cities": ["Spb"],
        "content": "content",
        "limit": 200,
        "locales": ["US"],
        "computed": {"promo.fs": 100, "total": 200},
        "name": "filter_group_1",
        "state": "NEW",
        "efficiency_time": ["12:00", "13:00"],
        "efficiency_date": ["2021-01-12", "2021-01-13"]
    }')::jsonb,
    ('{}')::jsonb,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 13
    7,
    ('{
        "channel": "FS",
        "cities": ["Spb"],
        "content": "content",
        "limit": 200,
        "locales": [],
        "name": "filter_group_1",
        "state": "NEW"
    }')::jsonb,
    ('{}')::jsonb,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 14
    7,
    ('{
        "channel": "FS",
        "cities": ["Msk"],
        "content": "content",
        "limit": 200,
        "locales": [],
        "name": "filter_group_2",
        "state": "NEW"
    }')::jsonb,
    ('{}')::jsonb,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 15
    8,
    ('{
        "channel": "FS",
        "cities": ["Spb"],
        "content": "content",
        "limit": 0,
        "locales": [],
        "name": "filter_group_1",
        "state": "NEW"
    }')::jsonb,
    ('{}')::jsonb,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 16
    8,
    ('{
        "channel": "FS",
        "cities": ["Msk"],
        "computed": {"promo.fs": 200, "total": 200},
        "content": "content",
        "limit": 200,
        "locales": [],
        "name": "filter_group_2",
        "state": "NEW"
    }')::jsonb,
    ('{}')::jsonb,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 17
    9,
    ('{
        "column": "column",
        "values": ["value"],
        "limit": 200,
        "channel": "PUSH",
        "computed": {"promo.fs": 200, "total": 200},
        "content": "content",
        "name": "value_group_1",
        "state": "NEW"
    }')::jsonb,
    ('{}')::jsonb,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 18
    10,
    ('{
        "column": "column",
        "values": ["value"],
        "limit": 200,
        "channel": "PUSH",
        "computed": {"total": 200},
        "content": "content",
        "name": "value_group_1",
        "state": "NEW"
    }')::jsonb,
    ('{}')::jsonb,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
);

INSERT INTO crm_admin.campaign
(
    id,
    segment_id,
    name,
    entity_type,
    trend,
    kind,
    discount,
    state,
    owner_name,
    ticket,
    ticket_status,
    com_politic,
    created_at,
    updated_at
)
VALUES
(
    1,
    null,
    'Первая кампания',
    'User',
    'Направление или тип первой кампании',
    'Тип или подтип первой кампании',
    True,
    'NEW',
    'user1',
    'Тикет1',
    'Открыт',
    False,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
),
(
    6,
    1,
    'Шестая кампания',
    'User',
    'Направление или тип шестой кампании',
    'Тип или подтип шестой кампании',
    True,
    'SEGMENT_FINISHED',
    'user6',
    'Тикет6',
    'Открыт',
    False,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
),
(
    7,
    2,
    'Седьмая кампания',
    'User',
    'Направление или тип седьмой кампании',
    'Тип или подтип седьмой кампании',
    True,
    'SEGMENT_FINISHED',
    'user7',
    'Тикет7',
    'Открыт',
    False,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
),
(
    8,
    3,
    'Восьмая кампания',
    'User',
    'Направление или тип восьмой кампании',
    'Тип или подтип восьмой кампании',
    True,
    'NEW',
    'user8',
    'Тикет8',
    'Открыт',
    False,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
),
(
    9,
    4,
    'Девятая кампания',
    'User',
    'Направление или тип девятой кампании',
    'Тип или подтип девятой кампании',
    True,
    'NEW',
    'user9',
    'Тикет9',
    'Открыт',
    False,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
),
(
    10,
    5,
    'a driver campaign',
    'Driver',
    'trend',
    'kind',
    True,
    'SEGMENT_FINISHED',
    'user9',
    'ticket',
    'open',
    False,
    '2020-08-21 01:00:00',
    '2020-08-21 01:00:00'
),
(
    11,
    6,
    'a user campaign with communication policy on',
    'User',
    'trend',
    'kind',
    True,
    'NEW',
    'user',
    'ticket',
    'open',
    False,
    '2020-08-21 01:00:00',
    '2020-08-21 01:00:00'
),
(
    12,
    6,
    'a user campaign with communication policy off',
    'User',
    'trend',
    'kind',
    True,
    'NEW',
    'user',
    'ticket',
    'open',
    True,
    '2020-08-21 01:00:00',
    '2020-08-21 01:00:00'
),
(
    13,
    7,
    'new (not computed) groups',
    'User',
    'trend',
    'kind',
    True,
    'NEW',
    'user',
    'ticket',
    'open',
    True,
    '2021-03-09 01:00:00',
    '2021-03-09 01:00:00'
),
(
    14,
    8,
    'empty group',
    'User',
    'trend',
    'kind',
    True,
    'NEW',
    'user',
    'ticket',
    'open',
    True,
    '2021-03-09 01:00:00',
    '2021-03-09 01:00:00'
),
(
    15,
    9,
    'value groups',
    'User',
    'trend',
    'kind',
    True,
    'NEW',
    'user',
    'ticket',
    'open',
    True,
    '2021-03-09 01:00:00',
    '2021-03-09 01:00:00'
),
(
    16,
    10,
    'empty segment',
    'User',
    'trend',
    'kind',
    True,
    'GROUPS_READY',
    'user',
    'ticket',
    'open',
    True,
    '2021-03-09 01:00:00',
    '2021-03-09 01:00:00'
);
