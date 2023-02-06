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
    'segment#1',
    'home/taxi-crm/robot-crm-admin/segment_sample',
    'Share',
    20,
    '2020-06-09 01:00:00'
);

INSERT INTO crm_admin.campaign
(
    id,
    segment_id,
    state,
    name,
    entity_type,
    trend,
    kind,
    subkind,
    discount,
    owner_name,
    ticket,
    ticket_status,
    global_control,
    com_politic,
    created_at,
    updated_at,
    efficiency_start_time,
    efficiency_stop_time,
    is_regular,
    regular_start_time,
    regular_stop_time,
    extra_data_path,
    extra_data_key
)
VALUES
(
    1,
    1,
    'NEW',
    'Пользовательская кампания',
    'User',
    'Направление или тип пользовательской кампании',
    'Тип или подтип пользовательской кампании',
    'subkind',
    True,
    'user1',
    'user_ticket',
    'Открыт',
    True,
    True,
    '2020-01-01 00:00:00',
    '2020-01-01 00:00:00',
    '2020-01-20 00:00:00',
    '2020-01-01 00:00:00',
    False,
    Null,
    '2020-01-01 00:00:00',
    '//home/taxi-crm/robot-crm-admin/extra_data_invalid',
    Null
);
