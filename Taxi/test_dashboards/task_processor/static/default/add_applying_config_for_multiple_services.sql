INSERT INTO dashboards.configs (
    status,
    dashboard_name,
    layouts
)
VALUES (
    'applying',
    'nanny_taxi_test-service_stable',
    ARRAY[
        ROW('system', NULL)::dashboards.layout_t,
        ROW('rps_share', NULL)::dashboards.layout_t,
        ROW('http', NULL)::dashboards.layout_t
    ]
)
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
    ARRAY[(400, null), (401, null), (403, null), (404, null), (429, null)]::dashboards.custom_response_t[]
),
(
    2,
    '/ping',
    'GET',
    ARRAY[(400, null), (401, null), (403, null), (404, null), (429, null)]::dashboards.custom_response_t[]
)
;

INSERT INTO dashboards.configs_handlers_link (
    config_id,
    handler_id
)
VALUES
(1, 1),
(1, 2)
;

INSERT INTO dashboards.branches_configs_link (
    service_branch_id,
    config_id
)
VALUES
(1, 1),
(2, 1)
;
