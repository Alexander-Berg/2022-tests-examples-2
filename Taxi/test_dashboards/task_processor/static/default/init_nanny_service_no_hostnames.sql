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
    ARRAY[]::text[],
    ROW('taxi_test-service_stable', 'nanny')
)
;
