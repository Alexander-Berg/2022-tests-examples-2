INSERT INTO crm_admin.campaign
(
    id,
    name,
    entity_type,
    trend,
    kind,
    discount,
    state,
    ticket,
    created_at
)
VALUES
(
    1,
    'campain #1',
    'User',
    'trend',
    'kind',
    True,
    'READY',
    'ticket',
    '2020-10-26 01:00:00'
),
(
    2,
    'campain #2',
    'Driver',
    'trend',
    'kind',
    True,
    'READY',
    'ticket',
    '2020-10-26 01:00:00'
),
(
    3,
    'campain #3',
    'Driver',
    'trend',
    'kind',
    True,
    'READY',
    'ticket',
    '2020-10-26 01:00:00'
),
(
    4,
    'campain #4',
    'Driver',
    'trend',
    'kind',
    True,
    'SEGMENT_CALCULATING',
    'ticket',
    '2020-10-26 01:00:00'
),
(
    5,
    'campain #5',
    'Driver',
    'trend',
    'kind',
    True,
    'READY',
    'ticket',
    '2020-10-26 01:00:00'
);


INSERT INTO crm_admin.operations(
    campaign_id,
    operation_name,
    submission_id,
    operation_type,
    status,
    started_at,
    finished_at
)
VALUES
(
    -- id: 1
    1,  -- campaign_id
    'new opearation',
    null, -- submission_id
    null, -- operation_type
    null, -- status
    '2020-10-26 02:00:00',
    null  -- finished_at
),
(
    -- id: 2
    1,  -- campaign_id
    'running operation',
    'submission id',
    'yql',
    'RUNNING',
    '2020-10-26 02:00:00',
    null  -- finished_at
),
(
    -- id: 3
    1,  -- campaign_id
    'finished operation',
    'submission id',
    'yql',
    'COMPLETED',
    '2020-10-26 02:00:00',
    '2020-10-26 03:00:00'
),
(
    -- id: 4
    2,  -- campaign_id
    'running operation',
    'submission id',
    'spark',
    'RUNNING',
    '2020-10-26 02:00:00',
    null  -- finished_at
),
(
    -- id: 5
    3,  -- campaign_id
    'finished operation, non-empty operation type',
    'submission id',
    'spark',
    'COMPLETED',
    '2020-10-26 02:00:00',
    '2020-10-26 03:00:00'
),
(
    -- id: 6
    3,  -- campaign_id
    'finished operation, empty operation type',
    'submission id',
    null,
    null,
    '2020-10-26 02:00:00',
    '2020-10-26 03:00:00'
),
(
    -- id: 7
    4,  -- campaign_id
    'runnining segment computations',
    'submission id',
    'yql',
    'RUNNING',
    '2020-10-26 02:00:00',
    null  -- finished_at
),
(
    -- id: 8
    5,  -- campaign_id
    'running operation',
    '00000000-0000-0000-0000-000000000000',
    'segment_splitter',
    'RUNNING',
    '2020-10-26 02:00:00',
    null  -- finished_at
);
