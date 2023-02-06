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
    'campain #1',
    'User',
    'trend',
    'kind',
    True,
    'READY',
    'ticket',
    '2020-10-26 01:00:00'
);


INSERT INTO crm_admin.operations
(
    campaign_id,
    operation_name,
    submission_id,
    operation_type,
    status,
    extra_data,
    started_at,
    finished_at
)
VALUES
(
    -- id: 1
    1, -- campaign_id
    'user-yql-operation',
    'submission_id',
    'yql',
    'RUNNING',
    ('{"key": "value"}'::jsonb),
    '2020-10-26 02:00:00',
    null
);
