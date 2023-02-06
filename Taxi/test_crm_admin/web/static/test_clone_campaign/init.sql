INSERT INTO crm_admin.segment
(
    -- id,
    yql_shared_url,
    yt_table,
    mode,
    control,
    aggregate_info,
    created_at
)
VALUES
(
    -- 1,  -- id
    'yql_shared_url',
    'yt_table',
    'Share',
    20,
    ('{"size": 1000}')::jsonb,
    '2021-02-03 01:00:00'
),
(
    -- 2,  -- id
    'yql_shared_url',
    'yt_table',
    'Share',
    20,
    null,
    '2021-02-03 01:00:00'
),
(
    -- 3,  -- id
    'yql_shared_url',
    'yt_table',
    'Share',
    20,
    null,
    '2021-02-03 01:00:00'
),
(
    -- 4,  -- id
    'yql_shared_url',
    'yt_table',
    'Share',
    20,
    null,
    '2021-02-03 01:00:00'
),
(
    -- 4,  -- id
    'yql_shared_url',
    'yt_table',
    'Share',
    20,
    null,
    '2021-02-03 01:00:00'
);


INSERT INTO crm_admin.group
(
    -- id,
    segment_id,
    params,
    yql_shared_url,
    created_at,
    updated_at
)
VALUES
(
    -- 1,  -- id
    1,  -- segment_id
    ('{"name": "group_1", "state": "SENT", "share": 20, "channel": "PUSH", "content": "push message", "sent": 10}')::jsonb,
    'yql_shared_url',
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- 2,  -- id
    1,  -- segment_id
    ('{"name": "group_2", "state": "HOLD", "share": 30, "channel": "DEVNULL", "content": "push message", "sent": 10}')::jsonb,
    'yql_shared_url',
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- 3,  -- id
    4,  -- segment_id
    ('{"name": "group_2", "state": "NEW", "share": 30, "channel": "LEGACYWALL", "feed_id": "feed_id"}')::jsonb,
    'yql_shared_url',
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- 4,  -- id
    5,  -- segment_id
    ('{"name": "group_1", "state": "SENT", "share": 20, "channel": "PUSH", "content": "push message", "sent": 10}')::jsonb,
    'yql_shared_url',
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
);


INSERT INTO crm_admin.campaign
(
    segment_id,
    name,
    entity_type,
    trend,
    kind,
    subkind,
    discount,
    state,
    settings,
    creative,
    global_control,
    efficiency,
    com_politic,
    is_regular,
    is_active,
    planned_start_date,
    created_at
)
VALUES
(
    -- 1,  -- id
    1,  -- segment_id
    'sent campaign',
    'User',
    'trend',
    'kind',
    'subkind',
    True,
    'SENDING_FINISHED',
    ('[{"fieldId": "field_oneshot", "value": "value"}]')::jsonb,
    'creative',
    True,  -- global_control
    True,  -- efficiency
    True,  -- com_politic
    False,  -- is_regular
    False,  -- is_active
    '2021-02-03',  -- planned_start_date
    '2021-02-03 01:00:00'
);

INSERT INTO crm_admin.campaign
(
    segment_id,
    name,
    entity_type,
    trend,
    discount,
    state,
    settings,
    creative,
    is_regular,
    is_active,
    created_at,
    efficiency_start_time,
    efficiency_stop_time,
    regular_start_time,
    regular_stop_time
)
VALUES
(
    -- 2,  -- id
    2,  -- segment_id
    'without groups',
    'User',
    'trend',
    True,
    'GROUPS_READY',
    ('[{"fieldId": "fieldId", "value": "value"}]')::jsonb,
    null,  -- creative
    False,  -- is_regular
    False,  -- is_active
    '2021-02-03 01:00:00',
    '2021-02-03 01:00:00',
    '2021-02-03 01:00:00',
    null,
    null
),
(
    -- 3,  -- id
    null,
    'without segment',
    'User',
    'trend',
    True,
    'READY',
    ('[{"fieldId": "fieldId", "value": "value"}]')::jsonb,
    null,  -- creative
    False,  -- is_regular
    False,  -- is_active
    '2021-02-03 01:00:00',
    null,
    null,
    null,
    null
),
(
    -- 4,  -- id
    null,
    'new campaign',
    'User',
    'trend',
    True,
    'NEW',
    null,
    null,  -- creative
    False,  -- is_regular
    False,  -- is_active
    '2021-02-03 01:00:00',
    null,
    null,
    null,
    null
),
(
    -- 5,  -- id
    4,  -- segment_id
    'wall campaign',
    'Driver',
    'trend',
    True,
    'CAMPAIGN_APPROVED',
    null,
    null,  -- creative
    False,  -- is_regular
    False,  -- is_active
    '2021-02-03 01:00:00',
    null,
    null,
    null,
    null
),
(
    -- 6,  -- id
    5,  -- segment_id
    'regular campaign',
    'User',
    'trend',
    True,
    'CAMPAIGN_APPROVED',
    ('[{"fieldId": "field_regular", "value": "value"}]')::jsonb,
    null,  -- creative
    True,  -- is_regular
    False,  -- is_active
    '2021-02-03 01:00:00',
    null,
    null,
    '2021-02-03 01:00:00',
    '2021-02-03 01:00:00'
);

INSERT INTO crm_admin.quicksegment_schemas (
    audience,
    major_ver,
    minor_ver,
    name,
    format,
    body,
    created_at
)
VALUES
(
    'User',
    0,  -- major_ver
    123,  -- minor_ver
    'input_schema',
    'json',
    '[{"id": "field_regular", "campaign_type": "regular"}, {"id": "field_oneshot", "campaign_type": "oneshot"}]',
    '2020-11-24 01:00:00'
);
