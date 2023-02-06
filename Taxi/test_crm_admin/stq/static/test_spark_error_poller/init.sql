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
    created_at,
    error_code
)
VALUES
(
    1,
    'campain #1',
    'User',
    'trend',
    'kind',
    True,
    'SEGMENT_ERROR',
    'ticket',
    '2020-10-26 01:00:00',
    'POLLING_SPARK_LOG'
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
    '2020-10-26 01:00:00',
    'POLLING_SPARK_LOG'
);


INSERT INTO crm_admin.operations
(
    id,
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
    1, -- operation_id
    1, -- campaign_id
    'user-yql-operation',
    'submission_id',
    'yql',
    'ERROR',
    ('{"key": "value"}'::jsonb),
    '2020-10-26 02:00:00',
    '2020-10-26 03:00:00'
),
(
    2, -- operation_id
    2, -- campaign_id
    'user-yql-operation',
    'submission_id',
    'yql',
    'ERROR',
    ('{"key": "value"}'::jsonb),
    '2020-10-26 02:00:00',
    '2020-10-26 03:00:00'
);
