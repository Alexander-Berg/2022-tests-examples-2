INSERT INTO dashboards.service_branches (
    clown_branch_id,
    project_name,
    service_name,
    branch_name,
    group_info
)
VALUES (
    123,
    'taxi-devops',
    'test-service',
    'stable',
    ROW('test_service_stable', 'nanny')
)
;
