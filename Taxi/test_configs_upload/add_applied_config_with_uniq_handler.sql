INSERT INTO dashboards.configs (
    status,
    dashboard_name,
    layouts
)
VALUES (
    'applied',
    'nanny_taxi_test_service_stable',
    ARRAY[
        ROW('http', NULL)::dashboards.layout_t,
        ROW('system', NULL)::dashboards.layout_t,
        ROW('rps_share', NULL)::dashboards.layout_t
    ]
)
;

INSERT INTO dashboards.handlers (
    service_branch_id,
    endpoint,
    method
)
VALUES (
    1,
    '/do_stuff',
    'POST'
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
