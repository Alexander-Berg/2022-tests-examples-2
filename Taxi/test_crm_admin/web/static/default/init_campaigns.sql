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
);

INSERT INTO crm_admin.group_v2
(
    id,
    segment_id,
    creative_id,
    name,
    type,
    params,
    user_tags,
    created_at,
    updated_at
)
VALUES
(
    1,
    1,
    1,
    'UserGroup1',
    'SHARE',
    ('{"channel": "PUSH", "content": "push text", "name": "share_group_1", "share": 20, "send_at": "2019-11-20T04:00:00+03:00"}')::jsonb,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    2,
    1,
    1,
    'UserGroup1',
    'SHARE',
    ('{"channel": "FS", "content": "banner_id", "name": "share_group_2", "share": 10, "send_at": "2019-11-20T04:00:00+03:00"}')::jsonb,
    ('[{"validity_time": {
        "active_days": 5,
        "end_time": "12:00"
      }, "tag": "tag1", "service": "taxi"},
      {"finish_at": "2022-01-31T04:00:00+03:00", "tag": "tag2", "service": "taxi"}]')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    3,
    1,
    null,
    'UserGroup1',
    'SHARE',
    ('{"share": 10}')::jsonb,
    ('[{"validity_time": {
        "active_days": 5,
        "end_time": "12:00"
      }, "tag": "tag1", "service": "taxi"},
      {"finish_at": "2022-01-31T04:00:00+03:00", "tag": "tag2", "service": "taxi"}]')::jsonb,
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
    salt,
    error_code,
    error_description,
    created_at,
    updated_at,
    motivation_methods
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
    'salt',
    'SOME_ERROR',  -- error_code
    ('{"message": "content"}')::jsonb,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00',
    '{workshifts}'
),
(
    'Вторая кампания',
    'User',
    'Направление или тип второй кампании',
    'Тип или подтип второй кампании',
    True,
    'NEW',
    'user2',
    'Тикет2',
    'Закрыт',
    null,  -- salt
    null,  -- error_code
    null,  -- error_description
    '2019-03-21 01:00:00',
    '2019-03-21 01:00:00',
    null   -- motivation_methods
),
(
    'Третья кампания',
    'User',
    'Направление или тип третьей кампании',
    'Тип или подтип третьей кампании',
    True,
    'NEW',
    'user3',
    'Тикет3',
    'Решен',
    null,  -- salt
    null,  -- error_code
    null,  -- error_description
    '2019-03-22 01:00:00',
    '2019-03-22 01:00:00',
    null   -- motivation_methods
),
(
    'Четвертая кампания',
    'User',
    'Направление или тип четвертой кампании',
    'Тип или подтип четвертой кампании',
    True,
    'NEW',
    'user4',
    'Тикет4',
    'Открыт',
    null,  -- salt
    null,  -- error_code
    null,  -- error_description
    '2019-03-23 01:00:00',
    '2019-03-23 01:00:00',
    null   -- motivation_methods
),
(
    'Пятая кампания',
    'User',
    'Направление или тип пятой кампании',
    'Тип или подтип пятой кампании',
    True,
    'NEW',
    'user5',
    'Тикет5',
    'Открыт',
    null,  -- salt
    null,  -- error_code
    null,  -- error_description
    '2019-03-24 01:00:00',
    '2019-03-24 01:00:00',
    null   -- motivation_methods
);

INSERT INTO crm_admin.campaign
(
    name,
    specification,
    entity_type,
    trend,
    kind,
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
    'Шестая кампания',
    'Описание шестой кампании',
    'Driver',
    'Направление или тип шестой кампании',
    'Тип или подтип шестой кампании',
    True,
    'NEW',
    'user6',
    ('[
          {
            "fieldId": "field_1",
            "value": "value_1"
          },
          {
            "fieldId": "field_2",
            "value": "value_2"
          },
          {
            "fieldId": "field_3",
            "value": "value_3"
          },
          {
            "fieldId": "field_4",
            "value": false
          },
          {
            "fieldId": "field_5",
            "value": 5
          },
          {
            "fieldId": "field_6",
            "value": 66.6
          }
    ]')::jsonb,
    'Тикет6',
    'Открыт',
    'Шестой креатив',
    ARRAY ['test1_user1', 'test1_user2'],
    1,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
),
(
    'Седьмая кампания',
    'Описание седьмой кампании',
    'User',
    'Направление или тип седьмой кампании',
    'Тип или подтип седьмой кампании',
    True,
    'NEW',
    'user7',
    ('[]')::jsonb,
    'Тикет7',
    'Открыт',
    'Седьмой креатив',
    ARRAY ['test2_user1', 'test2_user2'],
    2,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
),
(
    'Восьмая кампания',
    'Описание восьмой кампании',
    'User',
    'Направление или тип восьмой кампании',
    'Тип или подтип восьмой кампании',
    True,
    'NEW',
    'user8',
    ('[]')::jsonb,
    'Тикет8',
    'Открыт',
    'Восьмой креатив',
    ARRAY ['test3_user1', 'test3_user2'],
    3,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
),
(
    'Девятая кампания',
    'Описание девятой кампании',
    'User',
    'Направление или тип девятой кампании',
    'Тип или подтип девятой кампании',
    True,
    'READY',
    'user9',
    ('[]')::jsonb,
    'Тикет9',
    'Открыт',
    'Девятый креатив',
    ARRAY ['test4_user1', 'test4_user2'],
    4,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
),
(
    -- campaing_id: 10
    'EatsUser campaign',
    'specification',
    'EatsUser',
    'trend',
    'kind',
    True,
    'NEW',
    'user10',
    ('[]')::jsonb,
    'ticket',
    'open',
    'creative',
    null,
    null,
    '2021-05-31 01:00:00',
    '2021-05-31 01:00:00'
);

INSERT INTO crm_admin.campaign
(
    id,
    name,
    entity_type,
    trend,
    kind,
    discount,
    state,
    owner_name,
    ticket,
    ticket_status,
    salt,
    error_code,
    error_description,
    created_at,
    updated_at,
    motivation_methods,
    is_communications_limited,
    communications_limit
)
VALUES
(
    -- campaing_id: 123
    123,
    '123 кампания',
    'User',
    'Направление или тип 123 кампании',
    'Тип или подтип 123 кампании',
    True,
    'NEW',
    'user1',
    'Тикет1',
    'Открыт',
    'salt123',
    'SOME_ERROR',  -- error_code
    ('{"message": "content"}')::jsonb,
    '2021-03-20 01:00:00',
    '2021-03-20 01:00:00',
    '{workshifts}',
    True, -- is_communications_limited
    11 -- communications_limit
);

INSERT INTO crm_admin.ticket_status
(
    status_name,
    status_order
)
VALUES
(
    'Открыт',
    1
),
(
    'Закрыт',
    2
);
