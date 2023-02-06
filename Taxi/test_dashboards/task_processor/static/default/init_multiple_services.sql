INSERT INTO dashboards.service_branches (
    clown_branch_id,
    project_name,
    service_name,
    branch_name,
    hostnames,
    group_info
)
VALUES (
    123,
    'taxi-devops',
    'test-service',
    'stable',
    ARRAY['test-service.taxi.yandex.net'],
    ROW('taxi_test-service_stable', 'nanny')
),
(
    321,
    'taxi-devops',
    'test-service-2',
    'stable',
    ARRAY['test-service-2.taxi.yandex.net'],
    ROW('taxi_test-service-2_stable', 'nanny')
)
;
