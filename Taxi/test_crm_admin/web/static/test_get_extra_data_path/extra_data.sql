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
    'segment1_yql_shred_link',
    'segment1_yt_table',
    ('{}')::jsonb,
    'Share',
    20,
    '2019-11-20 01:00:00'
),
(
    2,
    'segment2_yql_shred_link',
    'segment2_yt_table',
    ('{}')::jsonb,
    'Share',
    20,
    '2019-11-20 01:00:00'
),
(
    3,
    'segment3_yql_shred_link',
    'segment3_yt_table',
    ('{}')::jsonb,
    'Share',
    20,
    '2019-11-20 01:00:00'
);


INSERT INTO crm_admin.campaign
(
    id,
    extra_data_path,
    segment_id,
    name,
    entity_type,
    trend,
    kind,
    subkind,
    discount,
    state,
    owner_name,
    ticket,
    ticket_status,
    global_control,
    com_politic,
    created_at,
    updated_at
)
VALUES
(
    1,
    NULL,
    1,
    'Пользовательская кампания',
    'User',
    'Направление или тип пользовательской кампании',
    'Тип или подтип пользовательской кампании',
    'subkind',
    True,
    'NEW',
    'user1',
    'user_ticket',
    'Открыт',
    True,
    True,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
),
(
    2,
    '//extra_data_path',
    2,
    'Водительская кампания',
    'Driver',
    'Направление или тип водительской кампании',
    'Тип или подтип водительской кампании',
    'subkind',
    False,
    'NEW',
    'driver2',
    'driver_ticket',
    'Открыт',
    False,
    False,
    '2019-03-21 01:00:00',
    '2019-03-21 01:00:00'
),
(
    3,
    NULL,
    1,
    'Пользовательская кампания',
    'User',
    'trend_1',
    'other_kind',
    'subkind_1_1_1',
    True,
    'NEW',
    'user1',
    'user_ticket',
    'Открыт',
    True,
    True,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
);
