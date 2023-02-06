INSERT INTO dashboards.service_branches (
    clown_branch_id,
    project_name,
    service_name,
    branch_name,
    hostnames,
    group_info
)
VALUES (
    321,
    'eda',
    'user-api',
    'stable',
    ARRAY['user_api.taxi.yandex.net'],
    ROW('taxi_user_api', 'conductor')
)
;
