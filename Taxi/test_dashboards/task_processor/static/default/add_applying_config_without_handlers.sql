INSERT INTO dashboards.configs (
    status,
    dashboard_name,
    layouts
)
VALUES (
    'applying',
    'eda_conductor_taxi_user_api',
    ARRAY[
        ROW('system', NULL)::dashboards.layout_t,
        ROW('lxc_container', NULL)::dashboards.layout_t,
        ROW(
            'include',
            '{
                "title": "Stats",
                "path": "cashback/cashback_line_graph.json",
                "row_panels": 3,
                "variables": [[{"title": "Orders processing"}]]
            }'::JSONB)::dashboards.layout_t,
        ROW('http', NULL)::dashboards.layout_t
    ]
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
