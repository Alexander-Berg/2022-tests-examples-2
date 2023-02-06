INSERT INTO dashboards.configs (
    status,
    dashboard_name,
    layouts
)
VALUES (
    'applied',
    'nanny_taxi_test-service_stable',
    ARRAY[
        ROW('system', NULL)::dashboards.layout_t,
        ROW('rps_share', NULL)::dashboards.layout_t,
        ROW('http', NULL)::dashboards.layout_t,
        ROW('distlock_worker', '{"workers": [{"id": "worker-id"}]}'::jsonb)::dashboards.layout_t
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
    '/get_stuff',
    'GET',
    ARRAY[(400, null), (401, null), (403, null), (404, null), (429, null)]::dashboards.custom_response_t[]
)
;

INSERT INTO dashboards.configs_handlers_link (
    config_id,
    handler_id
)
VALUES (
    currval(pg_get_serial_sequence('dashboards.configs', 'id')),
    currval(pg_get_serial_sequence('dashboards.handlers', 'id'))
)
;

INSERT INTO dashboards.branches_configs_link (
    service_branch_id,
    config_id
)
VALUES (
    1,
    currval(pg_get_serial_sequence('dashboards.configs', 'id'))
)
;
