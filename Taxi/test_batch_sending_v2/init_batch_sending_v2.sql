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
    ('{"channel_name": "user_push", "content": "user push text"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    2,  -- id
    'creative 2',
    ('{"channel_name": "user_promo_fs", "content": "user_fs_id"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    3,  -- id
    'creative 3',
    ('{"channel_name": "user_promo_notification", "content": "user_notification_id"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    4,  -- id
    'creative 4',
    ('{"channel_name": "user_promo_card", "content": "user_card_id"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    5,  -- id
    'creative 5',
    ('{"channel_name": "user_sms", "content": "user sms text"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    6,  -- id
    'creative 6',
    ('{"channel_name": "driver_push", "content": "driver push text", "code": 100}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    7,  -- id
    'creative 7',
    ('{"channel_name": "driver_sms", "content": "driver sms text"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    8,  -- id
    'creative 8',
    ('{"channel_name": "driver_wall", "content": "driver wall text"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    9,  -- id
    'creative 9',
    ('{"channel_name": "eatsuser_push", "content": "zuser push text"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    10,  -- id
    'creative 10',
    ('{"channel_name": "eatsuser_push", "content": "eatsuser push text"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    11,  -- id
    'creative 11',
    ('{"channel_name": "eatsuser_sms", "content": "eatsuser sms text"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
);

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

INSERT INTO crm_admin.group_v2
(
    id,
    segment_id,
    creative_id,
    name,
    type,
    params,
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
    ('{"deeplink": "user push deeplink", "share": 10}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    2,
    1,
    2,
    'UserGroup2',
    'SHARE',
    ('{"days_count": 7, "time_until": "17:17" ,"send_at": "2019-11-20T04:00:00+03:00", "share": 10}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    3,
    1,
    3,
    'UserGroup3',
    'SHARE',
    ('{"channel": "promo.notification", "content": "user_notification_id", "days_count": 8, "time_until": "18:18" ,"send_at": "2019-11-20T04:00:00+03:00", "share": 10}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    4,
    1,
    4,
    'UserGroup4',
    'SHARE',
    ('{"days_count": 9, "time_until": "19:19" ,"send_at": "2019-11-20T04:00:00+03:00", "share": 10}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    5,
    1,
    5,
    'UserGroup5',
    'SHARE',
    ('{"share": 10}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    6,
    2,
    6,
    'DriverGroup1',
    'SHARE',
    ('{"deeplink": "driver push deeplink", "share": 10}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    7,
    2,
    7,
    'DriverGroup2',
    'SHARE',
    ('{"channel": "SMS", "content": "driver sms text", "share": 10}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    8,
    2,
    8,
    'DriverGroup3',
    'SHARE',
    ('{"feed_id": "1001", "days_count": 11, "time_until": "11:11", "share": 10}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    9,
    3,
    9,
    'ZuserGroup1',
    'SHARE',
    ('{"deeplink": "zuser push deeplink", "share": 10}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    10,
    4,
    10,
    'EatsUserGroup1',
    'SHARE',
    ('{"deeplink": "eatsuser push deeplink", "share": 10}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    11,
    4,
    11,
    'EatsUserGroup2',
    'SHARE',
    ('{"channel": "SMS", "content": "eatsuser sms text", "share": 10}')::jsonb,
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
    extra_data_path,
    is_communications_limited,
    communications_limit
)
VALUES
(
    8,
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
    'extra_data_path7',
    True,
    999
);

INSERT INTO crm_admin.group_v2
(
    id,
    segment_id,
    creative_id,
    name,
    type,
    params,
    promocode_settings,
    user_tags,
    created_at,
    updated_at
)
VALUES
(
    12,
    4,
    1,
    'UserGroup12',
    'SHARE',
    ('{"deeplink": "user push deeplink", "share": 10}')::jsonb,
    null,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    13,
    4,
    2,
    'UserGroup13',
    'SHARE',
    ('{"days_count": 7, "time_until": "17:17" ,"send_at": "2019-11-20T04:00:00+03:00", "share": 10}')::jsonb,
    ('{
        "active_days": 123,
        "finish_at": "2022-01-31T01:00:00+00:00",
        "series": "promocode123",
        "service": "eats"
    }')::jsonb,
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    14,
    4,
    1,
    'UserGroup14',
    'SHARE',
    ('{"deeplink": "user push deeplink", "share": 10}')::jsonb,
    null,
    ('[{"validity_time": {
          "active_days": 5,
          "end_time": "12:00"
        }, "tag": "tag1", "service": "taxi"},
      {"finish_at": "2022-01-31T04:00:00+03:00", "tag": "tag2", "service": "taxi"}]')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    15,
    4,
    NULL,
    'UserGroup15',
    'SHARE',
    ('{"deeplink": "user push deeplink", "share": 10}')::jsonb,
    null,
    ('[{"validity_time": {
          "active_days": 5,
          "end_time": "12:00"
        }, "tag": "tag1", "service": "taxi"},
      {"finish_at": "2022-01-31T04:00:00+03:00", "tag": "tag2", "service": "taxi"}]')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
);
