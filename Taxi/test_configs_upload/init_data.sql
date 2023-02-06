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
    'test_service',
    'stable',
    ARRAY['test_service.taxi.yandex.net'],
    ROW('test_service_stable', 'nanny')
)
;
