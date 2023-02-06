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
),
(
    4,
    'segment4_yql_shred_link',
    'segment4_yt_table',
    ('{}')::jsonb,
    'Share',
    20,
    '2019-11-20 01:00:00'
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
    ('{"name": "UserGroup1", "channel": "PUSH", "content": "user push text", "deeplink": "user push deeplink", "share": 10}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    2,
    1,
    ('{"name": "UserGroup2", "channel": "promo.fs", "content": "user_fs_id", "days_count": 7, "time_until": "17:17" ,"send_at": "2019-11-20T04:00:00+03:00", "share": 10}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    3,
    1,
    ('{"name": "UserGroup3", "channel": "promo.notification", "content": "user_notification_id", "days_count": 8, "time_until": "18:18" ,"send_at": "2019-11-20T04:00:00+03:00", "share": 10}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    4,
    1,
    ('{"name": "UserGroup4", "channel": "promo.card", "content": "user_card_id", "days_count": 9, "time_until": "19:19" ,"send_at": "2019-11-20T04:00:00+03:00", "share": 10}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    5,
    1,
    ('{"name": "UserGroup5", "channel": "SMS", "content": "user sms text", "share": 10}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    6,
    2,
    ('{"name": "DriverGroup1", "channel": "PUSH", "content": "driver push text", "deeplink": "driver push deeplink", "share": 10}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    7,
    2,
    ('{"name": "DriverGroup2","channel": "SMS", "content": "driver sms text", "share": 10}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    8,
    2,
    ('{"name": "DriverGroup3","channel": "LEGACYWALL", "content": "driver wall text", "feed_id": "1001", "days_count": 11, "time_until": "11:11", "share": 10}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    9,
    3,
    ('{"name": "ZuserGroup1", "channel": "PUSH", "content": "zuser push text", "deeplink": "zuser push deeplink", "share": 10}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    10,
    4,
    ('{"name": "EatsUserGroup1", "channel": "PUSH", "content": "eatsuser push text", "deeplink": "eatsuser push deeplink", "share": 10}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    11,
    4,
    ('{"name": "EatsUserGroup2", "channel": "SMS", "content": "eatsuser sms text", "share": 10}')::jsonb,
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
    subkind,
    discount,
    state,
    owner_name,
    ticket,
    ticket_status,
    global_control,
    com_politic,
    created_at,
    updated_at,
    extra_data_path
)
VALUES
(
    1,
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
    '2020-03-20 01:00:00',
    null
),
(
    2,
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
    '2019-03-21 01:00:00',
    'extra_data_path2'
),
(
    3,
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
    '2020-03-20 01:00:00',
    'extra_data_path3'
),
(
    4,
    1,
    'Пользовательская кампания',
    'User',
    'trend_1',
    'kind_1_1',
    'other_subkind',
    True,
    'NEW',
    'user1',
    'user_ticket',
    'Открыт',
    True,
    True,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00',
    'extra_data_path4'
),
(
    5,
    1,
    'Пользовательская кампания',
    'User',
    'trend_1',
    'kind_1_1',
    'subkind_1_1_1',
    True,
    'NEW',
    'user1',
    'user_ticket',
    'Открыт',
    True,
    True,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00',
    'extra_data_path5'
),
(
    6,
    3,
    'Zпользовательская кампания',
    'Zuser',
    'Направление или тип zпользовательской кампании',
    'Тип или подтип zпользовательской кампании',
    'subkind',
    True,
    'NEW',
    'zuser1',
    'zuser_ticket',
    'Открыт',
    True,
    True,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00',
    'extra_data_path6'
),
(
    7,
    4,
    'Кампания еды',
    'EatsUser',
    'Направление или тип кампании еды',
    'Тип или подтип кампании еды',
    'subkind',
    True,
    'NEW',
    'eatsuser1',
    'eatsuser_ticket',
    'Открыт',
    True,
    True,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00',
    'extra_data_path7'
);
