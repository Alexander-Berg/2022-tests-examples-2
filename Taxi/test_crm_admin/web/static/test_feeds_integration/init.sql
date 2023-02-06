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
    '',
    '',
    ('{}')::jsonb,
    'Share',
    10,
    '2019-11-20 01:00:00'
),
(
    2,
    '',
    '',
    ('{}')::jsonb,
    'Share',
    20,
    '2019-11-20 01:00:00'
),
(
    3,
    '',
    '',
    ('{}')::jsonb,
    'Share',
    30,
    '2019-11-20 01:00:00'
),
(
    4,
    '',
    '',
    ('{}')::jsonb,
    'Share',
    40,
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
    ('{"name": "Campaign1Group1", "channel": "PUSH", "content": "push1text", "share": 10}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    2,
    1,
    ('{"name": "Campaign1Group2","channel": "SMS", "content": "sms1text", "share": 10}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    3,
    1,
    ('{"name": "Campaign1Group3","channel": "LEGACYWALL", "content": "wall1text", "feed_id": "1001", "days_count": 11, "time_until": "20:20", "share": 10}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    4,
    2,
    ('{"name": "Campaign2Group4", "channel": "PUSH", "content": "push2text", "share": 20}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    5,
    2,
    ('{"name": "Campaign2Group5","channel": "SMS", "content": "sms2text", "share": 20}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    6,
    2,
    ('{"name": "Campaign2Group6","channel": "LEGACYWALL", "content": "wall2text", "feed_id": "2001", "days_count": 22, "time_until": "20:20", "share": 20}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    7,
    3,
    ('{"name": "Campaign3Group7", "channel": "PUSH", "content": "push3text", "share": 30}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    8,
    3,
    ('{"name": "Campaign3Group8","channel": "SMS", "content": "sms3text", "share": 30}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    9,
    3,
    ('{"name": "Campaign3Group9","channel": "LEGACYWALL", "content": "wall3text", "feed_id": "3001", "days_count": 33, "time_until": "20:20", "share": 30}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    10,
    4,
    ('{"name": "Campaign4Group10", "channel": "PUSH", "content": "push4text", "share": 40}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    11,
    4,
    ('{"name": "Campaign4Group11","channel": "SMS", "content": "sms4text", "share": 40}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    12,
    4,
    ('{"name": "Campaign4Group12","channel": "LEGACYWALL", "content": "wall4text", "feed_id": "4001", "days_count": 44, "time_until": "20:20", "share": 40}')::jsonb,
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
    updated_at
)
VALUES
(
    1,
    1,
    'Campaign_1',
    'Driver',
    'Направление1',
    'Тип1',
    'Подтип1',
    False,
    'NEW',
    'driver1',
    'driver_ticket1',
    'Открыт',
    False,
    False,
    '2019-03-21 01:00:00',
    '2019-03-21 01:00:00'
),
(
    2,
    2,
    'Campaign_2',
    'Driver',
    'Направление2',
    'Тип2',
    'Подтип2',
    False,
    'NEW',
    'driver2',
    'driver_ticket2',
    'Открыт',
    False,
    False,
    '2019-03-21 01:00:00',
    '2019-03-21 01:00:00'
),
(
    3,
    3,
    'Campaign_3',
    'Driver',
    'Направление3',
    'Тип3',
    'Подтип3',
    False,
    'NEW',
    'driver3',
    'driver_ticket3',
    'Открыт',
    False,
    False,
    '2019-03-21 01:00:00',
    '2019-03-21 01:00:00'
),
(
    4,
    4,
    'Campaign_4',
    'Driver',
    'Направление4',
    'Тип4',
    'Подтип4',
    False,
    'NEW',
    'driver4',
    'driver_ticket4',
    'Открыт',
    False,
    False,
    '2019-03-21 01:00:00',
    '2019-03-21 01:00:00'
);
