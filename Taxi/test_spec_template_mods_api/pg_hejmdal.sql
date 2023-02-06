insert into circuit_schemas (id, description, circuit_schema, updated) values
(
'schema_test', 'test',$$
{
  "name": "test",
  "type": "schema",
  "wires": [
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
      "alpha": 0.7
    },
    {
      "id": "usage_out_of_limits_alert",
      "type": "out_of_bounds_state",
      "debug": [
        "state"
      ],
      "fixed_upper_bound": 90,
      "alert_text_template": "Высокое использование CPU: {value:.3f}%",
      "yield_state_on_bounds_in": false
    },
    {
      "id": "low_usage_out_of_limits",
      "type": "out_of_bounds_state",
      "fixed_lower_bound": 5,
      "alert_text_template": "Низкое использование CPU: {value:.3f}%",
      "yield_state_on_bounds_in": false
    },
    {
      "id": "low_usage_minimal_qouta_filter",
      "type": "state_transistor",
      "debug": [
        "state"
      ],
      "lower": 1.1,
      "default_state": "Ok"
    }
  ],
  "out_points": [
    {
      "id": "alert1",
      "type": "bypass"
    },
    {
      "id": "alert2",
      "type": "bypass"
    }
  ],
  "entry_points": [
    {
      "id": "entry1",
      "type": "data_entry_point",
      "debug": [
        "data"
      ]
    },
    {
      "id": "entry2",
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
insert into services (id, name, cluster_type, updated, deleted, project_id,
                      project_name, maintainers) values
(2, 'test_service2', 'nanny', now() at time zone 'utc', false, -1, 'test_project',
 '{}');

insert into branches (id, service_id, env, direct_link)
values (1111, 1, 'stable', 'test_service_stable_branch');

insert into branch_hosts (host_name, branch_id)
values ('test_service_stable_branch_host_name_1', 1111);
