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
    'test1_yt_table',
    ('{"size": 1000}')::jsonb,
    'Filter',
    10,
    '2021-01-21 11:00:00'
),
(
    2,
    '',
    'test2_yt_table',
    ('{"size": 1000}')::jsonb,
    'Filter',
    10,
    '2021-01-21 11:00:00'
),
(
    3,
    '',
    'test3_yt_table',
    ('{"size": 1000}')::jsonb,
    'Filter',
    10,
    '2021-01-21 11:00:00'
),
(
    4,
    '',
    'test4_yt_table',
    ('{"size": 1000}')::jsonb,
    'Filter',
    10,
    '2021-01-21 11:00:00'
),
(
    5,
    '',
    'test5_yt_table',
    ('{"size": 1000}')::jsonb,
    'Filter',
    10,
    '2021-01-21 11:00:00'
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
        "state": "NEW",
        "computed": {"total": 5000}
    }')::jsonb,
    'yql_shared_url',
    '2021-01-21 11:00:00',
    '2021-01-21 11:00:00'
),
(
    2,
    1,
     ('{
        "channel": "PUSH",
        "share": 10,
        "content": "bla_2",
        "name": "gr2",
        "state": "EFFICIENCY_SCHEDULED",
        "computed": {"total": 6000}
    }')::jsonb,
    null,
    '2021-01-21 11:00:00',
    '2021-01-21 11:00:00'
),
(
    3,
    1,
    ('{
        "channel": "PUSH",
        "share": 10,
        "content": "bla_3",
        "name": "gr3",
        "state": "EFFICIENCY_SENDING",
        "computed": {"total": 7000}
    }')::jsonb,
    null,
    '2021-01-21 11:00:00',
    '2021-01-21 11:00:00'
),
(
    4,
    1,
    ('{
        "channel": "PUSH",
        "share": 10,
        "content": "bla_4",
        "name": "gr4",
        "state": "EFFICIENCY_SKIPPED_SENDING",
        "computed": {"total": 8000}
    }')::jsonb,
    null,
    '2021-01-21 11:00:00',
    '2021-01-21 11:00:00'
),
(
    5,
    1,
    ('{
        "channel": "PUSH",
        "share": 10,
        "content": "bla_5",
        "name": "gr5",
        "state": "EFFICIENCY_DENIED",
        "computed": {"total": 1000}
    }')::jsonb,
    'yql_shared_url',
    '2021-01-21 11:00:00',
    '2021-01-21 11:00:00'
),
(
    6,
    1,
    ('{
        "channel": "PUSH",
        "share": 10,
        "content": "bla_6",
        "name": "gr6",
        "state": "EFFICIENCY_ANALYSIS",
        "computed": {"total": 1000}
    }')::jsonb,
    'yql_shared_url',
    '2021-01-21 11:00:00',
    '2021-01-21 11:00:00'
),
(
    7,
    1,
    ('{
        "channel": "PUSH",
        "share": 10,
        "content": "bla_7",
        "name": "gr7",
        "state": "SCHEDULED",
        "computed": {"total": 1000}
    }')::jsonb,
    'yql_shared_url',
    '2021-01-21 11:00:00',
    '2021-01-21 11:00:00'
),
(
    8,
    1,
    ('{
        "channel": "PUSH",
        "share": 10,
        "content": "bla_8",
        "name": "gr8",
        "state": "SENDING",
        "computed": {"total": 1000}
    }')::jsonb,
    'yql_shared_url',
    '2021-01-21 11:00:00',
    '2021-01-21 11:00:00'
),
(
    9,
    1,
    ('{
        "channel": "PUSH",
        "share": 10,
        "content": "bla_9",
        "name": "gr9",
        "state": "SENT",
        "computed": {"total": 1000}
    }')::jsonb,
    'yql_shared_url',
    '2021-01-21 11:00:00',
    '2021-01-21 11:00:00'
),
(
    10,
    1,
    ('{
        "channel": "PUSH",
        "share": 10,
        "content": "bla_10",
        "name": "gr10",
        "state": "HOLD",
        "computed": {"total": 1000}
    }')::jsonb,
    'yql_shared_url',
    '2021-01-21 11:00:00',
    '2021-01-21 11:00:00'
),
(
    11,
    1,
    ('{
        "channel": "PUSH",
        "share": 10,
        "content": "bla_11",
        "name": "gr11",
        "state": "ERROR",
        "computed": {"total": 1000}
    }')::jsonb,
    'yql_shared_url',
    '2021-01-21 11:00:00',
    '2021-01-21 11:00:00'
),
(
    20,
    2,
    ('{
        "channel": "PUSH",
        "share": 10,
        "content": "bla_20",
        "name": "gr20",
        "state": "NEW",
        "computed": {"total": 5000}
    }')::jsonb,
    'yql_shared_url',
    '2021-01-21 11:00:00',
    '2021-01-21 11:00:00'
),
(
    21,
    2,
     ('{
        "channel": "PUSH",
        "share": 10,
        "content": "bla_21",
        "name": "gr21",
        "state": "EFFICIENCY_SCHEDULED",
        "computed": {"total": 6000}
    }')::jsonb,
    null,
    '2021-01-21 11:00:00',
    '2021-01-21 11:00:00'
),
(
    23,
    2,
    ('{
        "channel": "PUSH",
        "share": 10,
        "content": "bla_23",
        "name": "gr23",
        "state": "SENT",
        "computed": {"total": 1000}
    }')::jsonb,
    'yql_shared_url',
    '2021-01-21 11:00:00',
    '2021-01-21 11:00:00'
),
(
    30,
    3,
    ('{
        "channel": "PUSH",
        "share": 10,
        "content": "bla_30",
        "name": "gr30",
        "state": "SCHEDULED",
        "computed": {"total": 5000}
    }')::jsonb,
    'yql_shared_url',
    '2021-01-21 11:00:00',
    '2021-01-21 11:00:00'
),
(
    31,
    3,
     ('{
        "channel": "PUSH",
        "share": 10,
        "content": "bla_31",
        "name": "gr31",
        "state": "SENT",
        "computed": {"total": 6000}
    }')::jsonb,
    null,
    '2021-01-21 11:00:00',
    '2021-01-21 11:00:00'
),
(
    40,
    4,
    ('{
        "channel": "PUSH",
        "share": 10,
        "content": "bla_40",
        "name": "gr40",
        "state": "NEW",
        "computed": {"total": 5000}
    }')::jsonb,
    'yql_shared_url',
    '2021-01-21 11:00:00',
    '2021-01-21 11:00:00'
),
(
    41,
    4,
     ('{
        "channel": "PUSH",
        "share": 10,
        "content": "bla_41",
        "name": "gr41",
        "state": "SENDING",
        "computed": {"total": 6000}
    }')::jsonb,
    null,
    '2021-01-21 11:00:00',
    '2021-01-21 11:00:00'
),
(
    50,
    5,
    ('{
        "channel": "PUSH",
        "share": 10,
        "content": "bla_50",
        "name": "gr50",
        "state": "SCHEDULED",
        "computed": {"total": 5000}
    }')::jsonb,
    'yql_shared_url',
    '2021-01-21 11:00:00',
    '2021-01-21 11:00:00'
),
(
    51,
    5,
     ('{
        "channel": "PUSH",
        "share": 10,
        "content": "bla_51",
        "name": "gr51",
        "state": "SENT",
        "computed": {"total": 6000}
    }')::jsonb,
    null,
    '2021-01-21 11:00:00',
    '2021-01-21 11:00:00'
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
    updated_at
)
VALUES
(
    1,
    1,
    'campaign',
    'User',
    'trend',
    'kind',
    True,
    'NEW',
    'user',
    'ticket',
    'Открыт',
    False,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
),
(
    2,
    2,
    'campaign',
    'User',
    'trend',
    'kind',
    True,
    'NEW',
    'user',
    'ticket',
    'Открыт',
    False,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
),
(
    3,
    3,
    'campaign',
    'User',
    'trend',
    'kind',
    True,
    'NEW',
    'user',
    'ticket',
    'Открыт',
    False,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
),
(
    4,
    4,
    'campaign',
    'User',
    'trend',
    'kind',
    True,
    'NEW',
    'user',
    'ticket',
    'Открыт',
    False,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
),
(
    5,
    5,
    'campaign',
    'User',
    'trend',
    'kind',
    True,
    'NEW',
    'user',
    'ticket',
    'Открыт',
    False,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
);


INSERT INTO crm_admin.campaign
(
    id,
    segment_id,
    name,
    entity_type,
    trend,
    discount,
    state,
    is_regular,
    is_active,
    schedule,
    created_at,
    ticket
)
VALUES
(
    6,  -- id
    1,  -- segment_id
    'active regular campaign',
    'User',
    'trend',
    True,  -- discount
    'SCHEDULED',
    True,  -- is_regular
    True,  -- is_active
    '1 12 * * *',  -- schedule
    '2021-01-26 01:00:00',
    'ticket'
),
(
    7,  -- id
    1,  -- segment_id
    'not yet active regular campagin',
    'User',
    'trend',
    True,  -- discount
    'SCHEDULED',
    True,  -- is_regular
    False,  -- is_active
    '1 12 * * *',  -- schedule
    '2021-01-26 01:00:00',
    'ticket'
),
(
    8,  -- id
    1,  -- segment_id
    'canceled regular camapaign',
    'User',
    'trend',
    True,  -- discount
    'SCHEDULED',
    True,  -- is_regular
    False,  -- is_active
    '1 12 * * *',  -- schedule
    '2021-01-26 01:00:00',
    'ticket'
);


INSERT INTO crm_admin.schedule
(
    campaign_id,
    scheduled_for
)
VALUES
(
    8,  -- campaign_id
    '2021-01-26 12:00:00'
);
