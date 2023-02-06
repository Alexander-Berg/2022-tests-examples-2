-- insert service
insert into services (id, name, cluster_type, updated, deleted, project_id,
                      project_name, maintainers) values
(1, 'test_service', 'nanny', now() at time zone 'utc', false, -1, 'test_project',
 '{}'),
(2, 'test_service_no_stable_branch', 'nanny', now() at time zone 'utc', false, -1, 'test_project',
 '{}');

-- insert stable branch
insert into branches (id, service_id, env, direct_link) values
(11, 1, 'stable', 'test_branch_stable_1');

-- insert schema template
insert into circuit_schemas (id, description, circuit_schema, type, custom) values
('template_test', 'Schema template for testing', $$
{
    "name": "Custom check template: threshold",
    "type": "template",
    "wires": [
        {"to": "average", "from": "usage", "type": "data"},
        {"to": "threshold", "from": "average", "type": "data"},
        {"to": "interval", "from": "threshold", "type": "state"},
        {"to": "alert", "from": "interval", "type": "state"}
    ],
    "blocks": [
    {
        "id": "average",
        "type": "fair_quantile_window",
        "level": 0.5,
        "window_sec": "$window_sec",
        "max_samples": 10000,
        "min_samples": "$min_samples"
    },
    {
        "id": "threshold",
        "type": "out_of_bounds_state",
        "fixed_upper_bound": "$fixed_upper_bound",
        "alert_text_template": "$alert_format",
        "yield_state_on_bounds_in": false
    },
    {
        "id": "interval",
        "type": "schmitt_state_window",
        "lower_time_ms": "$lower_time_ms",
        "upper_time_ms": "$upper_time_ms"
    }],
    "out_points": [
        {"id": "alert", "type": "state_out_point", "debug": ["state"]}
    ],
    "used_params": {
        "window_sec": {
            "type": "number",
            "required": true
        },
        "min_samples": {
            "type": "number",
            "required": true
        },
        "alert_format": {
            "type": "string",
            "default": "Значение метрики превысило пороговое значение: {value:.1f} > {bound:.1f}"
        },
        "lower_time_ms": {
            "type": "number",
            "required": true
        },
        "upper_time_ms": {
            "type": "number",
            "required": true
        },
        "fixed_upper_bound": {
            "type": "number",
            "required": true
        }
    },
    "entry_points": [
        {"id": "usage", "type": "data_entry_point"}
    ],
    "history_data_duration_sec": "$window_sec"
}$$::jsonb,
'template', true
);

-- insert schema
insert into circuit_schemas (id, description, circuit_schema, type, custom) values
('schema_custom_check_1', 'Schema for testing',$$
{
    "name": "Custom Metrics 1",
    "type": "schema",
    "use_template": "template_test",
    "override_params": {
        "window_sec": 5,
        "min_samples": 60,
        "lower_time_ms": 0,
        "upper_time_ms": 5000,
        "fixed_upper_bound": 100
  }
}$$::jsonb,
'schema', true
);

-- custom checks
insert into custom_checks (name, description, service_id, schema_id, flows)
values (
           'test_custom_check_name',
           'TEST custom check',
           1,
           'schema_custom_check_1',
           $${
             "usage": {
               "project": "taxi",
               "program": "series_sum({project='taxi', cluster='production_uservices', service='uservices', application='eats-surge-resolver', sensor='surge-stats.count_missing_places.1m', group='test-group_stable|test-group_pre_stable', host='test-host.yp-c.yandex.net'})"
             }
           }$$::jsonb);
