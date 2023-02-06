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
            "PUSH": {
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
),
(
    2,  -- id
    'creative 2',
    ('{"channel_name": "user_promo_fs", "content": "banner_id"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    3,  -- id
    'creative 3',
    ('{"channel_name": "user_promo_fs", "content": "banner_id"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    4,  -- id
    'creative 4',
    ('{"channel_name": "user_promo_fs", "content": "banner_id"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    5,  -- id
    'creative 5',
    ('{"channel_name": "user_push", "content": "push text"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    6,  -- id
    'creative 6',
    ('{"channel_name": "user_promo_fs", "content": "banner_id"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    7,  -- id
    'creative 7',
    ('{"channel_name": "user_push", "content": "push text"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    8,  -- id
    'creative 8',
    ('{"channel_name": "user_push", "content": "push text"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    9,  -- id
    'creative 9',
    ('{"channel_name": "user_push", "content": "push text"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    10,  -- id
    'creative 10',
    ('{"channel_name": "driver_push", "code": 1300, "content": "push text"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    11,  -- id
    'creative 11',
    ('{"channel_name": "driver_wall", "content": "banner_id"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    12,  -- id
    'creative 12',
    ('{"channel_name": "user_promo_fs", "content": "content"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    13,  -- id
    'creative 13',
    ('{"channel_name": "user_promo_fs", "content": "content"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    14,  -- id
    'creative 14',
    ('{"channel_name": "user_promo_fs", "content": "content"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    15,  -- id
    'creative 15',
    ('{"channel_name": "user_promo_fs", "content": "content"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    16,  -- id
    'creative 16',
    ('{"channel_name": "user_promo_fs", "content": "content"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    17,  -- id
    'creative 17',
    ('{"channel_name": "user_push", "content": "content"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    18,  -- id
    'creative 18',
    ('{"channel_name": "user_push", "content": "content"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    101,  -- id
    'creative 101',
    ('{"channel_name": "user_push", "content": "push text"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    102,  -- id
    'creative 102',
    ('{"channel_name": "user_promo_fs", "content": "banner_id"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    103,  -- id
    'creative 103',
    ('{"channel_name": "user_promo_fs", "content": "banner_id"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    104,  -- id
    'creative 104',
    ('{"channel_name": "user_promo_fs", "content": "banner_id"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    105,  -- id
    'creative 105',
    ('{"channel_name": "user_push", "content": "push text"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    106,  -- id
    'creative 106',
    ('{"channel_name": "user_promo_fs", "content": "banner_id"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    107,  -- id
    'creative 107',
    ('{"channel_name": "user_push", "content": "push text"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    108,  -- id
    'creative 108',
    ('{"channel_name": "user_push", "content": "push text"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    109,  -- id
    'creative 109',
    ('{"channel_name": "user_push", "content": "push text"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    117,  -- id
    'creative 109',
    ('{"channel_name": "user_push", "content": "push text"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
);

INSERT INTO crm_admin.group_v2
(
    creative_id,
    segment_id,
    name,
    state,
    type,
    params,
    promocode_settings,
    user_tags,
    sending_stats,
    computed,
    efficiency_time,
    efficiency_date,
    send_at,
    yql_shared_url,
    created_at,
    updated_at
)
VALUES
(
    -- id: 1
    1,
    1,
    'share_group_1',
    'NEW',
    'SHARE',
    ('{
        "share": 20
    }')::jsonb,
    ('{
        "active_days": 123,
        "finish_at": "2022-01-31T01:00:00+00:00",
        "series": "promocode123",
        "service": "eats"
      }')::jsonb,
    null,
    null,
    null,
    '{"01:00", "02:00"}',
    '{"2021-01-01", "2021-01-02"}',
    '2019-11-20T01:00:00',
    'yql_shared_url',
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 2
    2,
    1,
    'share_group_2',
    'NEW',
    'SHARE',
    ('{
        "share": 10
    }')::jsonb,
    null,
    ('[{"validity_time": {
        "active_days": 5,
        "end_time": "12:00"
      }, "tag": "tag1", "service": "taxi"},
      {"finish_at": "2022-01-31T04:00:00+03:00", "tag": "tag2", "service": "taxi"}]')::jsonb,
    ('{}')::jsonb,
    null,
    '{"02:00", "03:00"}',
    '{"2021-01-02", "2021-01-03"}',
    '2019-11-20T01:00:00',
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 3
    3,
    1,
    'share_group_3',
    'NEW',
    'SHARE',
    ('{
        "computed_share": 10,
        "share": 10
    }')::jsonb,
    null,
    null,
    ('{"sent": 100, "failed": 50, "planned": 180, "skipped": 30, "finished_at": "2021-01-20T16:40:00+03:00"}')::jsonb,
    null,
    '{"03:00", "04:00"}',
    '{"2021-01-03", "2021-01-04"}',
    '2019-11-20T01:00:00',
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 4
    4,
    1,
    'share_group_4',
    'NEW',
    'SHARE',
    ('{
        "share": 10
    }')::jsonb,
    null,
    null,
    ('{"sent": 104, "failed": 54, "planned": 192, "skipped": 34, "finished_at": "2021-01-20T16:40:00+03:00"}')::jsonb,
    ('{"total": 200}')::jsonb,
    '{"04:00", "05:00"}',
    '{"2021-01-04", "2021-01-05"}',
    '2019-11-20T01:00:00',
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 5
    5,
    2,
    'filter_group_1',
    'SENT',
    'FILTER',
    ('{
        "cities": ["Москва", "Орел"],
        "limit": 1000,
        "locales": ["RU"]
    }')::jsonb,
    ('{
        "active_days": 123,
        "finish_at": "2022-01-31T01:00:00+00:00",
        "series": "promocode123",
        "service": "eats"
      }')::jsonb,
    null,
    ('{"sent": 100, "failed": 50, "planned": 180, "skipped": 30, "finished_at": "2021-01-20T16:40:00+03:00"}')::jsonb,
    null,
    '{"05:00", "06:00"}',
    '{"2021-01-05", "2021-01-06"}',
    null,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 6
    6,
    2,
    'filter_group_2',
    'SENT',
    'FILTER',
    ('{
        "cities": ["Минск", "Могилев", "Орша"],
        "limit": 500,
        "locales": ["RU", "BY"]
    }')::jsonb,
    null,
    null,
    ('{}')::jsonb,
    null,
    '{"06:00", "07:00"}',
    '{"2021-01-06", "2021-01-07"}',
    null,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 7
    7,
    2,
    'filter_group_3',
    'SENT',
    'FILTER',
    ('{
        "cities": ["Сызрань", "Рязань"],
        "limit": 200,
        "locales": ["US"]
    }')::jsonb,
    null,
    null,
    ('{}')::jsonb,
    null,
    '{"07:00", "08:00"}',
    '{"2021-01-07", "2021-01-08"}',
    null,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 8
    8,
    2,
    'filter_group_4',
    'SENT',
    'FILTER',
    ('{
        "cities": ["Сызрань", "Рязань"],
        "limit": 200,
        "locales": ["US"],
        "computed_limit": 210
    }')::jsonb,
    null,
    null,
    ('{}')::jsonb,
    null,
    '{"08:00", "09:00"}',
    '{"2021-01-08", "2021-01-09"}',
    null,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 9
    9,
    2,
    'filter_group_5',
    'SENT',
    'FILTER',
    ('{
        "cities": ["Сызрань", "Рязань"],
        "limit": 200,
        "locales": ["US"]
    }')::jsonb,
    null,
    ('[{"validity_time": {
        "active_days": 5,
        "end_time": "12:00"
      }, "tag": "tag1", "service": "taxi"},
      {"finish_at": "2022-01-31T04:00:00+03:00", "tag": "tag2", "service": "taxi"}]')::jsonb,
    ('{}')::jsonb,
    ('{"total": 210}')::jsonb,
    '{"09:00", "10:00"}',
    '{"2021-01-09", "2021-01-10"}',
    null,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 10
    10,
    5,
    'share_group_1',
    'NEW',
    'SHARE',
    ('{
        "share": 20
    }')::jsonb,
    null,
    null,
    ('{}')::jsonb,
    null,
    '{"10:00", "11:00"}',
    '{"2021-01-10", "2021-01-11"}',
    '2019-11-20T01:00:00',
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 11
    11,
    5,
    'share_group_2',
    'NEW',
    'SHARE',
    ('{
        "share": 10
    }')::jsonb,
    null,
    null,
    ('{}')::jsonb,
    ('{"total": 100}')::jsonb,
    '{"11:00", "12:00"}',
    '{"2021-01-11", "2021-01-12"}',
    '2019-11-20T01:00:00',
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 12
    12,
    6,
    'filter_group_1',
    'NEW',
    'FILTER',
    ('{
        "cities": ["Spb"],
        "limit": 200,
        "locales": ["US"]
    }')::jsonb,
    null,
    null,
    ('{}')::jsonb,
    ('{"promo.fs": 100, "total": 200}')::jsonb,
    '{"12:00", "13:00"}',
    '{"2021-01-12", "2021-01-13"}',
    null,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 13
    13,
    7,
    'filter_group_1',
    'NEW',
    'FILTER',
    ('{
        "cities": ["Spb"],
        "limit": 200,
        "locales": []
    }')::jsonb,
    null,
    null,
    ('{}')::jsonb,
    null,
    null,
    null,
    null,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 14
    14,
    7,
    'filter_group_2',
    'NEW',
    'FILTER',
    ('{
        "cities": ["Msk"],
        "limit": 200,
        "locales": []
    }')::jsonb,
    null,
    null,
    ('{}')::jsonb,
    null,
    null,
    null,
    null,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 15
    15,
    8,
    'filter_group_1',
    'NEW',
    'FILTER',
    ('{
        "cities": ["Spb"],
        "limit": 0,
        "locales": []
    }')::jsonb,
    null,
    null,
    ('{}')::jsonb,
    null,
    null,
    null,
    null,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 16
    16,
    8,
    'filter_group_2',
    'NEW',
    'FILTER',
    ('{
        "cities": ["Msk"],
        "limit": 200,
        "locales": []
    }')::jsonb,
    null,
    null,
    ('{}')::jsonb,
    ('{"promo.fs": 200, "total": 200}')::jsonb,
    null,
    null,
    null,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 17
    17,
    9,
    'value_group_1',
    'NEW',
    'VALUE',
    ('{
        "column": "column",
        "values": ["value"],
        "limit": 200
    }')::jsonb,
    ('{
        "active_days": 123,
        "finish_at": "2022-01-31T01:00:00+00:00",
        "series": "promocode123",
        "service": "eats"
      }')::jsonb,
    ('[{"validity_time": {
        "active_days": 5,
        "end_time": "12:00"
        }, "tag": "tag1", "service": "taxi"},
      {"finish_at": "2022-01-31T04:00:00+03:00", "tag": "tag2", "service": "taxi"}]')::jsonb,
    ('{}')::jsonb,
    ('{"promo.fs": 200, "total": 200}')::jsonb,
    null,
    null,
    null,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 18
    18,
    10,
    'value_group_1',
    'NEW',
    'VALUE',
    ('{
        "column": "column",
        "values": ["value"],
        "limit": 200
    }')::jsonb,
    null,
    null,
    ('{}')::jsonb,
    ('{"total": 200}')::jsonb,
    null,
    null,
    null,
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
),
(
    17,
    10,
    'empty segment',
    'User',
    'trend',
    'kind',
    True,
    'CAMPAIGN_APPROVED',
    'user',
    'ticket',
    'open',
    True,
    '2021-03-09 01:00:00',
    '2021-03-09 01:00:00'
);
