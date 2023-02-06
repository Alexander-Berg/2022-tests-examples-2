INSERT INTO dashboards.configs (
    status,
    dashboard_name,
    layouts,
    job_id
)
VALUES
(
    'applying',
    'nanny_taxi-devops_test-service_stable',
    ARRAY[
        ROW('http', NULL)::dashboards.layout_t,
        ROW('system', NULL)::dashboards.layout_t,
        ROW('rps_share', NULL)::dashboards.layout_t
    ],
    666
),
(
    'waiting',
    'nanny_taxi-devops_test-service_stable',
    ARRAY[
        ROW('http', NULL)::dashboards.layout_t,
        ROW('system', NULL)::dashboards.layout_t
    ],
    NULL
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
