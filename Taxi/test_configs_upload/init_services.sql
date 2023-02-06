INSERT INTO dashboards.service_branches (
    clown_branch_id,
    project_name,
    service_name,
    branch_name,
    group_info
)
VALUES (
    123,
    'taxi',
    'test-service-1',
    'stable',
    ROW('test-service-1_stable', 'nanny')
),
(
    234,
    'taxi-devops',
    'test-service-2',
    'stable',
    ROW('test-service-2_stable', 'nanny')
),
(
    345,
    'eda',
    'test-service-3',
    'stable',
    ROW('test-service-3_stable', 'nanny')
),
(
    456,
    'lavka',
    'test-service-4',
    'stable',
    ROW('test-service-4_stable', 'nanny')
)
;
