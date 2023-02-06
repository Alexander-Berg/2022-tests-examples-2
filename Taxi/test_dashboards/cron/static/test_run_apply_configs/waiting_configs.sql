INSERT INTO dashboards.configs (
    status,
    dashboard_name,
    layouts
)
VALUES (
    'waiting',
    'nanny_taxi-devops_test-service_stable',
    ARRAY[
        ROW('http', NULL)::dashboards.layout_t,
        ROW('system', NULL)::dashboards.layout_t,
        ROW('rps_share', NULL)::dashboards.layout_t
    ]
),
(
    'waiting',
    'nanny_taxi-devops_test-service_testing',
    ARRAY[
        ROW('http', NULL)::dashboards.layout_t,
        ROW('system', NULL)::dashboards.layout_t,
        ROW('rps_share', NULL)::dashboards.layout_t
    ]
)
;

INSERT INTO dashboards.branches_configs_link (
    service_branch_id,
    config_id
)
VALUES
(1, 1),
(2, 2)
;

INSERT INTO dashboards.handlers (
    service_branch_id,
    endpoint,
    method,
    custom_responses
)
VALUES (
    1,
    '/ping',
    'GET',
    ARRAY[]::dashboards.custom_response_t[]
),
(
    2,
    '/ping',
    'GET',
    ARRAY[]::dashboards.custom_response_t[]
),
(
    2,
    '/get_stuff',
    'GET',
    ARRAY[(403, null)]::dashboards.custom_response_t[]
)
;

INSERT INTO dashboards.configs_handlers_link (
    config_id,
    handler_id
)
VALUES
(1, 1),
(2, 2),
(2, 3)
;
