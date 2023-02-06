

INSERT INTO crm_admin.sending
(
    id,
    campaign_id,
    group_id,
    type,
    state,
    created_at,
    updated_at
)
VALUES
(
    1,
    1,
    1,
    'VERIFY',
    'FINISHED',
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    2,
    1,
    2,
    'VERIFY',
    'FINISHED',
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    3,
    1,
    3,
    'VERIFY',
    'FINISHED',
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    4,
    2,
    4,
    'PRODUCTION',
    'FINISHED',
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    5,
    2,
    5,
    'PRODUCTION',
    'FINISHED',
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    6,
    2,
    6,
    'PRODUCTION',
    'FINISHED',
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    7,
    3,
    7,
    'PRODUCTION',
    'FINISHED',
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    8,
    3,
    8,
    'PRODUCTION',
    'FINISHED',
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    9,
    3,
    9,
    'PRODUCTION',
    'FINISHED',
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
);

CREATE TABLE crm_admin.sending(
    id SERIAL PRIMARY KEY,
    campaign_id SERIAL NOT NULL,
    group_id SERIAL NOT NULL,
    type TEXT NOT NULL,
    state TEXT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE
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
    ('{"name": "UserGroup1", "share": 10, "state": "SENT"}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'

),
(
    2,
    1,
    ('{"name": "UserGroup1", "share": 10, "state": "SENT"}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    3,
    1,
    ('{"name": "UserGroup1", "share": 10, "state": "SENT"}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    4,
    2,
    ('{"name": "UserGroup1", "share": 10, "state": "SENT"}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    5,
    2,
    ('{"name": "UserGroup1", "share": 10, "state": "SENT"}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    6,
    2,
    ('{"name": "UserGroup1", "share": 10, "state": "ERROR"}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    7,
    3,
    ('{"name": "UserGroup1", "share": 10, "state": "SENT"}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    8,
    3,
    ('{"name": "UserGroup1", "share": 10, "state": "SENT"}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    9,
    3,
    ('{"name": "UserGroup1", "share": 10, "state": "HOLD"}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    10,
    4,
    ('{"name": "UserGroup1", "share": 10, "state": "SENT"}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    11,
    4,
    ('{"name": "UserGroup1", "share": 10, "state": "HOLD"}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    12,
    4,
    ('{"name": "UserGroup1", "share": 10, "state": "SENDING"}')::jsonb,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
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
    'yql_shred_link1',
    'yt_table1',
    ('{}')::jsonb,
    'Share',
    20,
    '2020-03-20 01:00:00'
),
(
    2,
    'yql_shred_link2',
    'yt_table2',
    ('{}')::jsonb,
    'Share',
    20,
    '2020-03-20 01:00:00'
),
(
    3,
    'yql_shred_link3',
    'yt_table3',
    ('{}')::jsonb,
    'Share',
    20,
    '2020-03-20 01:00:00'
),
(
    4,
    'yql_shred_link4',
    'yt_table4',
    ('{}')::jsonb,
    'Share',
    20,
    '2020-03-20 01:00:00'
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
    global_control,
    created_at,
    updated_at
)
VALUES
(
    1,
    1,
    'campaign1',
    'User',
    'trend1',
    'kind1',
    True,
    'PREPARING_SENDING_PROCESSING',
    'owner1',
    'ticket1',
    'Открыт',
    True,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
),
(
    2,
    2,
    'campaign2',
    'User',
    'trend2',
    'kind2',
    True,
    'PREPARING_SENDING_PROCESSING',
    'owner2',
    'ticket2',
    'Открыт',
    True,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
),
(
    3,
    3,
    'campaign3',
    'User',
    'trend3',
    'kind3',
    True,
    'PREPARING_SENDING_PROCESSING',
    'owner3',
    'ticket3',
    'Открыт',
    True,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
),
(
    4,
    4,
    'campaign4',
    'User',
    'trend4',
    'kind4',
    True,
    'PREPARING_SENDING_PROCESSING',
    'owner4',
    'ticket4',
    'Открыт',
    True,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
);
