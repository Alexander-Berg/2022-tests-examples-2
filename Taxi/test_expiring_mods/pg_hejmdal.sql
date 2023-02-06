insert into circuit_schemas (id, description, circuit_schema, updated) values
('schema_rtc_memory_usage_v2', 'RTC memory usage', $$
{
    "name": "RTC RAM usage",
    "type": "schema",
    "wires": [
        {
            "to": "avg_usage",
            "from": "usage",
            "type": "data"
        },
        {
            "to": "smooth_avg_usage",
            "from": "avg_usage",
            "type": "data"
        },
        {
            "to": "usage_out_of_limits_alert",
            "from": "smooth_avg_usage",
            "type": "data"
        },
        {
            "to": "alert",
            "from": "usage_out_of_limits_alert",
            "type": "state"
        },
        {
            "to": "low_usage_out_of_limits",
            "from": "smooth_avg_usage",
            "type": "data"
        },
        {
            "to": "low_usage_minimal_qouta_filter",
            "from": "low_usage_out_of_limits",
            "type": "state"
        },
        {
            "to": "low_usage_minimal_qouta_filter",
            "from": "limit",
            "type": "data"
        },
        {
            "to": "low_usage",
            "from": "low_usage_minimal_qouta_filter",
            "type": "state"
        }
    ],
    "blocks": [
        {
            "id": "avg_usage",
            "type": "avg_window",
            "duration_ms": 900000,
            "max_sample_size": 360
        },
        {
            "id": "smooth_avg_usage",
            "type": "smooth_data",
            "alpha": 0.7,
            "debug": [
               "data"
            ]
        },
        {
            "id": "usage_out_of_limits_alert",
            "type": "out_of_bounds_state",
            "debug": [
               "state"
            ],
            "fixed_upper_bound": 90,
            "alert_text_template": "Высокое использование памяти: {value:.3f}%",
            "yield_state_on_bounds_in": false
        },
        {
            "id": "low_usage_out_of_limits",
            "type": "out_of_bounds_state",
            "fixed_lower_bound": 5,
            "alert_text_template": "Низкое использование памяти: {value:.3f}%",
            "yield_state_on_bounds_in": false
        },
        {
            "id": "low_usage_minimal_qouta_filter",
            "type": "state_transistor",
            "debug": [
               "state"
            ],
            "lower": 4.1,
            "default_state": "Ok"
        }
    ],
    "out_points": [
        {
           "id": "alert",
            "type": "bypass"
        },
        {
            "id": "high_usage",
            "type": "bypass"
        },
        {
            "id": "low_usage",
            "type": "bypass"
        }
    ],
    "entry_points": [
        {
            "id": "limit",
            "type": "data_entry_point"
        },
        {
            "id": "usage",
            "type": "data_entry_point"
        }
    ],
    "history_data_duration_sec": 900
}
$$::JSONB, '1970-01-15T06:58:08.001+00:00'::TIMESTAMPTZ);

insert into services (id, name, cluster_type, updated, deleted, project_id,
                      project_name, maintainers) values
(1, 'test_service', 'nanny', now() at time zone 'utc', false, -1, 'test_project',
 '{}');
