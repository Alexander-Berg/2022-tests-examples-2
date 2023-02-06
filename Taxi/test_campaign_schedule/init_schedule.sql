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
    ('{"size": 1000}')::jsonb,
    'Share',
    10,
    '2021-01-01 01:00:00'
),
(
    2,
    'test2_yql_shred_link',
    'test2_yt_table',
    ('{"size": 2000}')::jsonb,
    'Filter',
    20,
    '2021-01-01 01:00:00'
),
(
    3,
    'test3_yql_shred_link',
    'test3_yt_table',
    ('{"size": 3000}')::jsonb,
    'Share',
    30,
    '2021-01-01 01:00:00'
),
(
    4,
    'test1_yql_shred_link',
    'test1_yt_table',
    ('{"size": 1000}')::jsonb,
    'Share',
    10,
    '2021-01-01 01:00:00'
),
(
    5,
    'test2_yql_shred_link',
    'test2_yt_table',
    ('{"size": 2000}')::jsonb,
    'Filter',
    20,
    '2021-01-01 01:00:00'
),
(
    6,
    'test3_yql_shred_link',
    'test3_yt_table',
    ('{"size": 3000}')::jsonb,
    'Share',
    30,
    '2021-01-01 01:00:00'
);

INSERT INTO crm_admin.group
(
    id,
    segment_id,
    params,
    yql_shared_url,
    created_at,
    updated_at
)
VALUES
(
    1,
    1,
    ('{
        "channel": "PUSH",
        "share": 10,
        "content": "bla_1",
        "name": "gr1",
        "state": "EFFICIENCY",
        "efficiency_time": ["10:00", "20:00"],
        "efficiency_date": ["2021-01-10", "2021-01-20"]
    }')::jsonb,
    'yql_shared_url',
    '2021-01-01 01:00:00',
    '2021-01-01 01:00:00'
),
(
    2,
    1,
     ('{
        "channel": "PUSH",
        "share": 10,
        "content": "bla_2",
        "name": "gr2",
        "state": "EFFICIENCY",
        "efficiency_time": ["11:00", "19:00"],
        "efficiency_date": ["2021-01-12", "2021-01-18"]
    }')::jsonb,
    null,
    '2021-01-01 01:00:00',
    '2021-01-01 01:00:00'
),
(
    3,
    2,
    ('{
        "channel": "PUSH",
        "share": 10,
        "content": "bla_3",
        "name": "gr3",
        "state": "EFFICIENCY",
        "efficiency_time": ["10:00", "20:00"],
        "efficiency_date": ["2021-01-12", "2021-01-18"]
    }')::jsonb,
    'yql_shared_url',
    '2021-01-01 01:00:00',
    '2021-01-01 01:00:00'
),
(
    4,
    2,
     ('{
        "channel": "PUSH",
        "share": 10,
        "content": "bla_4",
        "name": "gr4",
        "state": "EFFICIENCY",
        "efficiency_time": ["11:00", "19:00"],
        "efficiency_date": ["2021-01-10", "2021-01-20"]
    }')::jsonb,
    null,
    '2021-01-01 01:00:00',
    '2021-01-01 01:00:00'
),
(
    5,
    3,
    ('{
        "channel": "PUSH",
        "share": 10,
        "content": "bla_5",
        "name": "gr5",
        "state": "EFFICIENCY",
        "efficiency_time": ["10:00", "20:00"],
        "efficiency_date": ["2021-01-01", "2021-01-10"]
    }')::jsonb,
    'yql_shared_url',
    '2021-01-01 01:00:00',
    '2021-01-01 01:00:00'
),
(
    6,
    3,
     ('{
        "channel": "PUSH",
        "share": 10,
        "content": "bla_6",
        "name": "gr6",
        "state": "EFFICIENCY",
        "efficiency_time": ["11:00", "19:00"],
        "efficiency_date": ["2021-01-01", "2021-01-10"]
    }')::jsonb,
    null,
    '2021-01-01 01:00:00',
    '2021-01-01 01:00:00'
);

INSERT INTO crm_admin.campaign
(
    id,
    segment_id,
    name,
    entity_type,
    trend,
    kind,
    discount,
    state,
    owner_name,
    ticket,
    ticket_status,
    com_politic,
    created_at,
    updated_at,
    efficiency,
    is_regular,
    efficiency_start_time,
    efficiency_stop_time,
    schedule
)
VALUES
(
    1,
    1,
    'Campaign1',
    'User',
    'Trend1',
    'Kind1',
    True,
    'GROUPS_FINISHED',
    'user1',
    'Ticket1',
    'Открыт',
    False,
    '2021-01-01 01:00:00',
    '2021-01-01 01:00:00',
    True,
    False,
    '2021-01-10 10:00:00',
    '2021-01-20 20:00:00',
    '* * * * *'
),
(
    2,
    2,
    'Campaign2',
    'User',
    'Trend2',
    'Kind2',
    True,
    'VERIFY_FINISHED',
    'user2',
    'Ticket2',
    'Открыт',
    False,
    '2021-01-01 01:00:00',
    '2021-01-01 01:00:00',
    True,
    False,
    '2021-01-10 10:00:00',
    '2021-01-20 10:00:00',
    '* * * * *'
),
(
    3,
    3,
    'Campaign3',
    'User',
    'Trend3',
    'Kind3',
    True,
    'CAMPAIGN_APPROVED',
    'user3',
    'Ticket3',
    'Открыт',
    False,
    '2021-01-01 01:00:00',
    '2021-01-01 01:00:00',
    True,
    False,
    '2021-01-01 10:00:00',
    '2021-01-10 10:00:00',
    '* * * * *'
),
(
    4,
    4,
    'Campaign4',
    'User',
    'Trend4',
    'Kind4',
    True,
    'GROUPS_FINISHED',
    'user4',
    'Ticket4',
    'Открыт',
    False,
    '2021-01-01 01:00:00',
    '2021-01-01 01:00:00',
    False,
    True,
    '2021-01-10 10:00:00',
    '2021-01-20 20:00:00',
    '* * * * *'
),
(
    5,
    5,
    'Campaign2',
    'User',
    'Trend5',
    'Kind5',
    True,
    'VERIFY_FINISHED',
    'user5',
    'Ticket5',
    'Открыт',
    False,
    '2021-01-01 01:00:00',
    '2021-01-01 01:00:00',
    False,
    True,
    '2021-01-10 10:00:00',
    '2021-01-20 10:00:00',
    '* * * * *'
),
(
    6,
    6,
    'Campaign6',
    'User',
    'Trend6',
    'Kind6',
    True,
    'CAMPAIGN_APPROVED',
    'user6',
    'Ticket6',
    'Открыт',
    False,
    '2021-01-01 01:00:00',
    '2021-01-01 01:00:00',
    False,
    True,
    '2021-01-01 10:00:00',
    '2021-01-10 10:00:00',
    '* * * * *'
);
