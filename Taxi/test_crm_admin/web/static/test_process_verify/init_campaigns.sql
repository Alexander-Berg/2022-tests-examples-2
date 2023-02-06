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
    'shared link',
    'path/to/segment_2',
    ('{}')::jsonb,
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
);

INSERT INTO crm_admin.group_v2
(
    id,
    segment_id,
    creative_id,
    state,
    name,
    type,
    params,
    computed,
    user_tags,
    promocode_settings,
    created_at,
    updated_at
)
VALUES
(
    1,
    1,
    1,
    'NEW',
    'UserGroup1',
    'SHARE',
    ('{"channel": "PUSH", "content": "push text", "name": "share_group_1", "share": 20, "send_at": "2019-11-20T04:00:00+03:00"}')::jsonb,
    ('{"total": 100}')::jsonb,
    null,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    2,
    1,
    1,
    'NEW',
    'UserGroup1',
    'SHARE',
    ('{"channel": "FS", "content": "banner_id", "name": "share_group_2", "share": 10, "send_at": "2019-11-20T04:00:00+03:00"}')::jsonb,
    ('{"total": 100}')::jsonb,
    ('[{"validity_time": {
        "active_days": 5,
        "end_time": "12:00"
      }, "tag": "tag1", "service": "taxi"},
      {"finish_at": "2022-01-31T04:00:00+03:00", "tag": "tag2", "service": "taxi"}]')::jsonb,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    3,
    1,
    null,
    'NEW',
    'UserGroup1',
    'SHARE',
    ('{"share": 10}')::jsonb,
    ('{"total": 100}')::jsonb,
    ('[{"validity_time": {
        "active_days": 5,
        "end_time": "12:00"
      }, "tag": "tag1", "service": "taxi"},
      {"finish_at": "2022-01-31T04:00:00+03:00", "tag": "tag2", "service": "taxi"}]')::jsonb,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    4,
    2,
    1,
    'NEW',
    'UserGroup1',
    'SHARE',
    ('{"channel": "PUSH", "content": "push text", "name": "share_group_1", "share": 20, "send_at": "2019-11-20T04:00:00+03:00"}')::jsonb,
    ('{"total": 100}')::jsonb,
    null,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    5,
    2,
    1,
    'NEW',
    'UserGroup1',
    'SHARE',
    ('{"channel": "PUSH", "content": "push text", "name": "share_group_1", "share": 20, "send_at": "2019-11-20T04:00:00+03:00"}')::jsonb,
    ('{"total": 100}')::jsonb,
    null,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    6,
    2,
    1,
    'NEW',
    'UserGroup1',
    'SHARE',
    ('{"channel": "PUSH", "content": "push text", "name": "share_group_1", "share": 20, "send_at": "2019-11-20T04:00:00+03:00"}')::jsonb,
    ('{"total": 100}')::jsonb,
    null,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    7,
    1,
    1,
    'NEW',
    'UserGroup1',
    'SHARE',
    ('{"channel": "FS", "content": "banner_id", "name": "share_group_2", "share": 10, "send_at": "2019-11-20T04:00:00+03:00"}')::jsonb,
    ('{"total": 100}')::jsonb,
    null,
    '{"service": "eats", "series": "series"}'::jsonb,
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
    '2 кампания',
    'Описание 2 кампании',
    'Driver',
    'Направление или тип 2 кампании',
    'Тип или подтип 2 кампании',
    True,
    'GROUPS_FINISHED',
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
    'Тикет11',
    'Открыт',
    '11 креатив',
    ARRAY ['test1_user1', 'test1_user2'],
    1,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
);


INSERT INTO crm_admin.campaign
(   segment_id,
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
    test_users,
    created_at,
    updated_at
)
VALUES
(   2,
    'Третья кампания',
    'User',
    'Направление или тип первой кампании',
    'Тип или подтип первой кампании',
    True,
    'GROUPS_FINISHED',
    'user1',
    'Тикет1',
    'Открыт',
    'salt',
    '{"+79818241621"}',
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
),
(   2,
    'Четвертая кампания',
    'User',
    'Направление или тип первой кампании',
    'Тип или подтип первой кампании',
    True,
    'GROUPS_FINISHED',
    'user1',
    'Тикет1',
    'Открыт',
    'salt',
    '{"+79818241621"}',
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
),
(   2,
    'Пятая кампания',
    'User',
    'Направление или тип первой кампании',
    'Тип или подтип первой кампании',
    True,
    'GROUPS_FINISHED',
    'user1',
    'Тикет1',
    'Открыт',
    'salt',
    '{"+79818241621"}',
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
);
