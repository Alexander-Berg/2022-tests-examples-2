INSERT INTO crm_admin.segment
(
    id,
    yql_shared_url,
    yt_table,
    mode,
    control,
    created_at
)
VALUES
(
    1,
    'segment#1 shared link',
    'path/to/segment_1',
    'Share',
    20,
    '2020-06-09 01:00:00'
),
(
    3,
    'segment#3 shared link',
    'path/to/segment_3',
    'Share',
    20,
    '2020-06-09 01:00:00'
);


INSERT INTO crm_admin.group
(
    id,
    segment_id,
    params,
    created_at,
    updated_at
)
VALUES
(
    1,
    1,
    ('{"name": "group1", "share": 10, "deeplink": "taximeter://screen/main", "state": "NEW"}')::jsonb,
    '2020-10-01 01:00:00',
    '2020-10-01 01:00:00'
),
(
    2,
    1,
    ('{"name": "group2", "share": 10, "state": "NEW"}')::jsonb,
    '2020-10-01 01:00:00',
    '2020-10-01 01:00:00'
),
(
    3,
    1,
    ('{"name": "0_control", "share": 10, "deeplink": "taximeter://screen/main", "state": "NEW"}')::jsonb,
    '2020-10-01 01:00:00',
    '2020-10-01 01:00:00'
),
(
    4,
    1,
    ('{"name": "0_global_control", "share": 10, "state": "NEW"}')::jsonb,
    '2020-10-01 01:00:00',
    '2020-10-01 01:00:00'
);


INSERT INTO crm_admin.campaign
(
    id,
    segment_id,
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
    settings,
    created_at
)
VALUES
(
    1,
    1,
    'Первая кампания',
    'Описание первой кампании',
    'User',
    'Направление или тип первой кампании',
    'Тип или подтип первой кампании',
    True,
    'NEW',
    'user1',
    'Тикет1',
    'Первый креатив',
    ('[]')::jsonb,
    '2020-03-20 01:00:00'
),
(
    2,
    Null,
    'Вторая кампания',
    'Описание второй кампании',
    'User',
    'Направление или тип второй кампании',
    'Тип или подтип второй кампании',
    True,
    'NEW',
    'user2',
    'Тикет2',
    'Второй креатив',
    ('[]')::jsonb,
    '2019-03-21 01:00:00'
),
(
    3,
    3,
    'driver campaign',
    'a dirver campaing for segmenting tests',
    'Driver',
    'trend',
    'kind',
    True,
    'PREPARING_SEGMENT_CALCULATING',
    'some_user',
    'ticket',
    'some text',
    ('[]')::jsonb,
    '2020-07-13 01:00:00'
),
(
    4,
    3,
    'driver campaign',
    'a dirver campaing for segmenting tests',
    'Driver',
    'trend',
    'kind',
    True,
    'CANCELED',
    'some_user',
    'ticket',
    'some text',
    ('[]')::jsonb,
    '2020-07-13 01:00:00'
)
