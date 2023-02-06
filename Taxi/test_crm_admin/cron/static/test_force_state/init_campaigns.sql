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
    'salt',
    'SOME_ERROR',  -- error_code
    ('{"message": "content"}')::jsonb,
    '2020-01-20 01:00:00',
    '2020-03-20 01:00:00'
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
    '2019-03-21 01:00:00'
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
    '2019-03-22 01:00:00'
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
    '2019-03-23 01:00:00'
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
    '2019-03-24 00:59:00',
    '2019-03-24 01:00:00'
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
    '2020-01-20 01:00:00',
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
    'READY',
    'user8',
    ('[]')::jsonb,
    'Тикет8',
    'Открыт',
    'Восьмой креатив',
    ARRAY ['test3_user1', 'test3_user2'],
    3,
    '2020-01-20 01:00:00',
    '2020-02-20 01:00:00'
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
    is_regular
)
VALUES
(
    'Десятая кампания',
    'User',
    'Направление или тип десятой кампании',
    'Тип или подтип десятой кампании',
    True,
    'NEW',
    'user5',
    'Тикет5',
    'Открыт',
    null,  -- salt
    null,  -- error_code
    null,  -- error_description
    '2019-01-24 01:00:00',
    '2019-03-24 01:00:00',
    TRUE
),
(
    'Одинадцатая кампания',
    'User',
    'Направление или тип одинадцатой кампании',
    'Тип или подтип одинадцатой кампании',
    True,
    'NEW',
    'user5',
    'Тикет5',
    'Открыт',
    null,  -- salt
    null,  -- error_code
    null,  -- error_description
    '2019-01-24 01:00:00',
    '2020-03-24 01:00:00',
    TRUE
),
(
    'Двенадцатая кампания',
    'User',
    'Направление или тип двенадцатой кампании',
    'Тип или подтип двенадцатой кампании',
    True,
    'NEW',
    'user5',
    'Тикет5',
    'Открыт',
    null,  -- salt
    null,  -- error_code
    null,  -- error_description
    '2019-01-24 01:00:00',
    '2020-03-24 01:00:00',
    TRUE
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


TRUNCATE crm_admin.campaign_state_log;

INSERT INTO crm_admin.campaign_state_log
    (campaign_id, state_from, state_to, updated_at)
SELECT id, '', 'NEW', created_at + '3 hours' FROM crm_admin.campaign;

INSERT INTO crm_admin.campaign_state_log
    (campaign_id, state_from, state_to, updated_at)
SELECT id, 'NEW', state, updated_at + '3 hours' FROM crm_admin.campaign;

DELETE FROM crm_admin.campaign_state_log
WHERE campaign_id IN (7, 9, 11);
