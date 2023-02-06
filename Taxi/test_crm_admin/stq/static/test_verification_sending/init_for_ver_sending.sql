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
        ]
    }')::jsonb,
    'Share',
    10,
    '2019-11-20 01:00:00'
);

INSERT INTO crm_admin.group
(
    id,
    segment_id,
    yql_shared_url,
    params,
    created_at,
    updated_at
)
VALUES
(
    1,
    1,
    'test1_group_yql_shared_link',
    ('{"name": "group_1", "share": 20, "channel": "PUSH", "content": "push message"}')::jsonb,
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
    discount,
    state,
    owner_name,
    ticket,
    creative,
    test_users,
    segment_id,
    created_at
)
VALUES
(
	1,
    'Первая кампания',
    'Описание первой кампании',
    'User',
    'Направление или тип первой кампании',
    'Тип или подтип первой кампании',
    True,
    'GROUPS_FINISHED',
    'user1',
    'Тикет1',
    'Первый креатив',
    ARRAY ['test1_user1', 'test1_user2'],
    1,
    '2020-03-20 01:00:00'
);

INSERT INTO crm_admin.campaign
(
    id,
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
    created_at
)
VALUES
(
	2,
    'Вторая кампания',
    'Описание второй кампании',
    'User',
    'Направление или тип второй кампании',
    'Тип или подтип второй кампании',
    True,
    'GROUPS_FINISHED',
    'user2',
    'Тикет2',
    'Первый второй',
    '2020-03-20 01:00:00'
),
(
	3,
    'Третья кампания',
    'Описание третьей кампании',
    'User',
    'Направление или тип третьей кампании',
    'Тип или подтип третьей кампании',
    True,
    'NEW',
    'user3',
    'Тикет3',
    'Третий креатив',
    '2020-03-20 01:00:00'
);
