insert into services (id, name, cluster_type, updated, deleted, project_id,
                      project_name, maintainers, tvm_name) values
(1, 'test_service1', 'nanny', '1970-01-15T08:58:08.001+00:00', false, 39, 'test_project',
 '{}', 'test_service1'),
(2, 'test_service2', 'nanny', '1970-01-15T08:58:08.001+00:00', false, 39, 'test_project',
 '{}', 'test_service2'),
(3, 'test_service3', 'nanny', '1970-01-15T08:58:08.001+00:00', false, 39, 'test_project',
 '{}', 'test_service3'),
(4, 'test_db1', 'postgres', '1970-01-15T08:58:08.001+00:00', false, 39, 'test_project',
 '{}', null);

insert into branches (id, service_id, env, direct_link)
values (1111, 1, 'stable', 'test_service_stable_branch'),
(1112, 1, 'prestable', 'test_service_prestable_branch'),
(2222, 2, 'stable', 'test_service2_stable_branch'),
(4444, 4, 'stable', 'test_db_stable_branch');

insert into branch_hosts (host_name, branch_id)
values ('test_service_stable_branch_host_name_1', 1111),
('test_service_stable_branch_host_name_2', 1111),
('test_service_prestable_branch_host_name_2', 1112),
('test_db_stable_branch_host_name_1', 4444);



insert into circuit_states (circuit_id, out_point_id, alert_status,
                            incident_start_time, updated, description,
                            meta_data)
values ('test_service_stable_branch_host_name_1::rtc_memory_usage', 'alert', 'OK',
        null, now() at time zone 'utc',
        '', $$
        {
            "juggler_service_name": "hejmdal-bad-rps",
            "env": "stable",
            "service_id": 1,
            "out_point_id": "alert"
        }
        $$),
       ('test_service_stable_branch_host_name_1::rtc_memory_usage', 'low_usage', 'OK',
        null, now() at time zone 'utc',
        '', $$
        {"env": "stable", "service_id": 1, "out_point_id": "low_usage"}
        $$),
       ('test_service_stable_branch_host_name_1::rtc_memory_usage', 'high_usage', 'OK',
        null, now() at time zone 'utc',
        '', $$
        {"env": "stable", "service_id": 1, "juggler_service_name": "hejmdal-bad-rps", "out_point_id": "high_usage"}
        $$),
       ('test_service_stable_branch_host_name_2::rtc_memory_usage', 'alert', 'OK',
        null, now() at time zone 'utc',
        '', $$
        {
            "juggler_service_name": "hejmdal-bad-rps",
            "env": "stable",
            "service_id": 1,
            "out_point_id": "alert"
        }
        $$),
       ('test_db_stable_branch_host_name_1::pg_ram_usage', 'alert', 'WARN',
        null, now() at time zone 'utc',
        '', $$
        {"env": "stable", "service_id": 4, "juggler_service_name": "hejmdal-pg-ram-usage", "out_point_id": "alert"}
        $$);

insert into juggler_check_states (service, host, status, description, updated, changed) values
('some-juggler-check', 'test_service_stable_branch', 'WARN', 'some description',
 '1970-01-15T06:58:08.001+00:00'::TIMESTAMPTZ,
 '1970-01-15T06:58:08.001+00:00'::TIMESTAMPTZ),
('other-juggler-check', 'test_service2_stable_branch', 'CRIT', 'some description',
     '1970-01-15T06:58:08.001+00:00'::TIMESTAMPTZ,
     '1970-01-15T06:58:08.001+00:00'::TIMESTAMPTZ);

insert into circuit_schemas (id, description, circuit_schema, updated) values
('schema_rtc_memory_usage_v2', 'RTC memory usage',$$
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
$$::JSONB, '1970-01-15T06:58:08.001+00:00'::TIMESTAMPTZ),
 ('schema_pg_ram_usage', 'PG memory usage',$$
 {
   "blocks": [
     {
       "duration_ms": 900000,
       "id": "avg_usage",
       "max_sample_size": 360,
       "type": "avg_window"
     },
     {
       "alpha": 0.7,
       "debug": [
         "data"
       ],
       "id": "smooth_avg_usage",
       "type": "smooth_data"
     },
     {
       "alert_text_template": "Высокое использование памяти: {value:.1f}%",
       "debug": [
         "state"
       ],
       "fixed_upper_bound": 90,
       "id": "usage_out_of_limits_alert",
       "type": "out_of_bounds_state",
       "yield_state_on_bounds_in": false
     },
     {
       "alert_text_template": "Низкое использование памяти: {value:.1f}%",
       "fixed_lower_bound": 6,
       "id": "low_usage_out_of_limits",
       "type": "out_of_bounds_state",
       "yield_state_on_bounds_in": false
     },
     {
       "alert_text_template": "Высокое использование памяти: {value:.1f}%",
       "debug": [
         "state"
       ],
       "fixed_upper_bound": 90,
       "id": "high_usage_out_of_limits",
       "type": "out_of_bounds_state",
       "yield_state_on_bounds_in": false
     },
     {
       "debug": [
         "state"
       ],
       "default_state": "Ok",
       "id": "low_usage_minimal_qouta_filter",
       "lower": 4.1,
       "type": "state_transistor"
     }
   ],
   "entry_points": [
     {
       "id": "limit",
       "type": "data_entry_point"
     },
     {
       "id": "usage_prc",
       "type": "data_entry_point"
     }
   ],
   "history_data_duration_sec": 900,
   "name": "MDB RAM usage",
   "out_points": [
     {
       "id": "alert",
       "type": "state_out_point"
     },
     {
       "id": "low_usage",
       "type": "state_out_point"
     },
     {
       "id": "high_usage",
       "type": "state_out_point"
     }
   ],
   "type": "template",
   "wires": [
     {
       "from": "usage_prc",
       "to": "avg_usage",
       "type": "data"
     },
     {
       "from": "avg_usage",
       "to": "smooth_avg_usage",
       "type": "data"
     },
     {
       "from": "smooth_avg_usage",
       "to": "usage_out_of_limits_alert",
       "type": "data"
     },
     {
       "from": "usage_out_of_limits_alert",
       "to": "alert",
       "type": "state"
     },
     {
       "from": "smooth_avg_usage",
       "to": "low_usage_out_of_limits",
       "type": "data"
     },
     {
       "from": "low_usage_out_of_limits",
       "to": "low_usage_minimal_qouta_filter",
       "type": "state"
     },
     {
       "from": "limit",
       "to": "low_usage_minimal_qouta_filter",
       "type": "data"
     },
     {
       "from": "low_usage_minimal_qouta_filter",
       "to": "low_usage",
       "type": "state"
     },
     {
       "from": "smooth_avg_usage",
       "to": "high_usage_out_of_limits",
       "type": "data"
     },
     {
       "from": "high_usage_out_of_limits",
       "to": "high_usage",
       "type": "state"
     }
   ]
 }$$::JSONB, '1970-01-15T06:58:08.001+00:00'::TIMESTAMPTZ
 );
