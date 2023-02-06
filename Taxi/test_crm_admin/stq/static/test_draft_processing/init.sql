INSERT INTO crm_admin.segment
(
    yql_shared_url,
    yt_table,
    mode,
    control,
    created_at
)
VALUES
(
    -- id: 1
    'segment#1 shared link',
    'path/to/segment_1',
    'Share',
    20,
    '2020-06-09 01:00:00'
),
(
    -- id: 2
    'segment#2 shared link',
    'path/to/segment_2',
    'Share',
    20,
    '2020-06-09 01:00:00'
);


INSERT INTO crm_admin.creative
(
    name,
    params,
    created_at,
    updated_at
)
VALUES
(
    -- id: 1
    'creative 1',
    ('{"channel_name": "user_push", "content": "push text 1"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    -- id: 2
    'creative 2',
    ('{"channel_name": "user_push", "content": "push text 2"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    -- id: 3
    'creative 3',
    ('{"channel_name": "user_push", "content": "push text 3"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    -- id: 4
    'creative 4',
    ('{"channel_name": "user_push", "content": "push text 4"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    -- id: 5
    'creative 5',
    ('{"channel_name": "user_push", "content": "push text 5"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    -- id: 6
    'creative 6',
    ('{"channel_name": "user_push", "content": "push text 6"}')::jsonb,
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
    sending_stats,
    computed,
    efficiency_time,
    efficiency_date,
    send_at,
    yql_shared_url,
    created_at,
    updated_at,
    sent,
    sent_time
)
VALUES
(
    -- id: 1
    1,
    1,
    'share_group_1',
    null,
    'SHARE',
    ('{
        "share": 20
    }')::jsonb,
    null,
    null,
    '{"01:00", "02:00"}',
    '{"2021-01-01", "2021-01-02"}',
    '2019-11-20T01:00:00',
    'yql_shared_url',
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00',
    100,
    '2021-01-20T16:40:00'::timestamp
),
(
    -- id: 2
    2,
    1,
    'share_group_2',
    null,
    'SHARE',
    ('{
        "share": 10
    }')::jsonb,
    ('{}')::jsonb,
    null,
    '{"02:00", "03:00"}',
    '{"2021-01-02", "2021-01-03"}',
    '2019-11-20T01:00:00',
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00',
    100,
    '2021-01-20T16:40:00'::timestamp
),
(
    -- id: 3
    4,
    2,
    'share_group_3',
    null,
    'SHARE',
    ('{
        "computed_share": 10,
        "share": 10
    }')::jsonb,
    ('{"sent": 100, "failed": 50, "planned": 180, "skipped": 30, "finished_at": "2021-01-20T16:40:00+03:00"}')::jsonb,
    null,
    '{"03:00", "04:00"}',
    '{"2021-01-03", "2021-01-04"}',
    '2019-11-20T01:00:00',
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00',
    100,
    '2021-01-20T16:40:00'::timestamp
),
(
    -- id: 4
    5,
    2,
    'share_group_4',
    null,
    'SHARE',
    ('{
        "share": 10
    }')::jsonb,
    ('{"sent": 104, "failed": 54, "planned": 192, "skipped": 34, "finished_at": "2021-01-20T16:40:00+03:00"}')::jsonb,
    ('{"total": 200}')::jsonb,
    '{"04:00", "05:00"}',
    '{"2021-01-04", "2021-01-05"}',
    '2019-11-20T01:00:00',
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00',
    100,
    '2021-01-20T16:40:00'::timestamp
);


INSERT INTO crm_admin.campaign
(
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
    ticket_status,
    creative,
    settings,
    created_at,
    root_id,
    test_users,
    efficiency,
    is_regular,
    is_active,
    subkind,
    extra_data,
    extra_data_path,
    global_control,
    com_politic,
    tasks,
    planned_start_date,
    extra_data_key,
    schedule,
    regular_start_time,
    regular_stop_time,
    efficiency_start_time,
    efficiency_stop_time,
    motivation_methods,
    parent_id,
    child_id,
    version_state
)
VALUES
(
    -- id: 1
    1,
    'Первая кампания',
    'Описание первой кампании',
    'User',
    'promo',
    'Тип или подтип первой кампании',
    True,
    'NEW',
    'user1',
    'Тикет1',
    'Открыт',
    'Первый креатив',
    ('[]')::jsonb,
    '2020-03-20 01:00:00',
    1,
    '{"+79118464991"}',
    false,
    true,
    true,
    'money_geo',
    '{"analysts_summoned": "2021-12-03 13:40:55.031720"}'::jsonb,
    '//home/taxi-crm/robot-crm-admin/cmp_10247_extra_data',
    true,
    true,
    '{1}',
    '2021-12-12'::date,
    'extra_data_key',
    '0 12 * * *',
    '2022-02-01 00:59:00.100000'::timestamp,
    '2022-02-01 18:58:38.410000'::timestamp,
    null,
    null,
    '{"workshifts", "promocode", "priority"}',
    null,
    null,
    'ACTUAL'
),
(
    -- id: 2
    2,
    'Вторая кампания',
    'Описание второй кампании',
    'User',
    'promo',
    'Тип или подтип второй кампании',
    True,
    'NEW',
    'user2',
    'Тикет2',
    'Открыт',
    'второй креатив',
    ('[]')::jsonb,
    '2020-03-20 01:00:00',
    2,
    '{"+79118464991"}',
    false,
    true,
    true,
    'money_geo',
    '{"analysts_summoned": "2021-12-03 13:40:55.031720"}'::jsonb,
    '//home/taxi-crm/robot-crm-admin/cmp_10248_extra_data',
    true,
    true,
    '{1}',
    '2021-12-12'::date,
    'extra_data_key',
    '0 12 * * *',
    '2022-02-01 00:59:00.100000'::timestamp,
    '2022-02-01 18:58:38.410000'::timestamp,
    null,
    null,
    '{"workshifts", "promocode", "priority"}',
    null,
    3,
    'ACTUAL'
),
(
    -- id: 3
    null,
    'Вторая кампания',
    'Описание второй кампании',
    'User',
    'promo',
    'Тип или подтип второй кампании',
    True,
    'PREPARING_DRAFT',
    'trusienkodv',
    'Тикет2',
    'Открыт',
    'второй креатив',
    ('[]')::jsonb,
    '2020-03-20 01:00:00',
    2,
    '{"+79118464991"}',
    false,
    true,
    false,
    'money_geo',
    '{"analysts_summoned": "2021-12-03 13:40:55.031720"}'::jsonb,
    '//home/taxi-crm/robot-crm-admin/cmp_10248_extra_data',
    true,
    true,
    '{1}',
    '2021-12-12'::date,
    'extra_data_key',
    '0 12 * * *',
    '2022-02-01 00:59:00.100000'::timestamp,
    '2022-02-01 18:58:38.410000'::timestamp,
    null,
    null,
    '{"workshifts", "promocode", "priority"}',
    2,
    null,
    'DRAFT'
);


INSERT INTO crm_admin.campaign_creative_connection
(
    campaign_id,
    creative_id,
    created_at
)
VALUES
(
    -- id: 1
    1,
    1,
    '2021-02-03 01:00:00'
),
(
    -- id: 2
    1,
    2,
    '2021-02-03 01:00:00'
),
(
    -- id: 3
    1,
    3,
    '2021-02-03 01:00:00'
),
(
    -- id: 4
    2,
    4,
    '2021-02-03 01:00:00'
),
(
    -- id: 5
    2,
    5,
    '2021-02-03 01:00:00'
),
(
    -- id: 6
    2,
    6,
    '2021-02-03 01:00:00'
);



