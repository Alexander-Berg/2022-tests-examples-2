INSERT INTO crm_admin.nirvana_task
(
    campaign_id,
    campaign_task_id,
    description,
    state,
    instance_id,
    instance_status,
    instance_result,
    created_at,
    expires_at,
    updated_at
)
VALUES
(
    1,
    1,
    'описание 1',
    'STARTED',
    'new_instance_id1',
    'running',
    'undefined',
    '2019-11-20 01:00:00',
    '2019-11-21 01:00:00',
    '2019-11-20 01:00:00'
),
(
    2,
    1,
    'описание 1 2',
    'NEW',
    null,
    null,
    null,
    '2019-11-20 01:00:00',
    '2019-11-21 01:00:00',
    '2019-11-20 01:00:00'
),
(
    6,
    1,
    'описание 6',
    'NEW',
    null,
    null,
    null,
    '2019-11-20 01:00:00',
    '2019-11-21 01:00:00',
    '2019-11-20 01:00:00'
)
