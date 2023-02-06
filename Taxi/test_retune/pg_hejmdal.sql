-- Schemas: CPU, timings, aggregation

insert into circuit_schemas (id, description, circuit_schema, type) values
('schema_test', 'Schema for testing of hejmdal in testsuite',$$
 {
   "name": "schema_test",
   "type": "schema",
   "wires": [
     {
       "to": "entry1_oob",
       "from": "entry1",
       "type": "data"
     },
     {
       "to": "entry2_oob",
       "from": "entry2",
       "type": "data"
     },
     {
       "to": "alert1",
       "from": "entry1_oob",
       "type": "state"
     },
     {
       "to": "alert2",
       "from": "entry2_oob",
       "type": "state"
     }
   ],
   "blocks": [
     {
       "id": "entry1_oob",
       "type": "out_of_bounds_state",
       "fixed_upper_bound": 90,
       "yield_state_on_bounds_in": false
     },
     {
       "id": "entry2_oob",
       "type": "out_of_bounds_state",
       "fixed_lower_bound": 5,
       "yield_state_on_bounds_in": false
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
       "type": "data_entry_point"
     },
     {
       "id": "entry2",
       "type": "data_entry_point"
     }
   ],
   "history_data_duration_sec": 60
 }
 $$::JSONB, 'schema'),
('schema_rtc_cpu_usage_v2', 'RTC cpu usage',$$
{
  "blocks": [
    {
      "id": "smooth_avg_usage",
      "quartile": 0.5,
      "sample_size": 60,
      "type": "fair_quartile_sample"
    },
    {
      "alert_text_template": "Высокое использование CPU: {value:.1f}%",
      "debug": [
        "state"
      ],
      "fixed_upper_bound": 70,
      "id": "usage_out_of_limits_alert",
      "type": "out_of_bounds_state",
      "yield_state_on_bounds_in": false
    },
    {
      "alert_text_template": "Низкое использование CPU: {value:.1f}%",
      "fixed_lower_bound": 6,
      "id": "low_usage_out_of_limits",
      "type": "out_of_bounds_state",
      "yield_state_on_bounds_in": false
    },
    {
      "default_state": "Ok",
      "id": "low_usage_minimal_qouta_filter",
      "lower": 1.5,
      "type": "state_transistor"
    },
    {
      "alert_text_template": "Высокое использование CPU: {value:.1f}%",
      "debug": [
        "state"
      ],
      "fixed_upper_bound": 70,
      "id": "high_usage_out_of_limits",
      "type": "out_of_bounds_state",
      "yield_state_on_bounds_in": false
    }
  ],
  "entry_points": [
    {
      "id": "limit",
      "type": "data_entry_point"
    },
    {
      "debug": [
        "data"
      ],
      "id": "usage",
      "type": "data_entry_point"
    }
  ],
  "history_data_duration_sec": 900,
  "name": "RTC cpu usage",
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
  "type": "schema",
  "wires": [
    {
      "from": "usage",
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
}
$$::JSONB, 'schema'),
('template_timings', 'tpl', $$
{
  "blocks": [
    {
      "base_term": 20,
      "coeff": 3,
      "id": "iqr_bounds",
      "sample_size": 60,
      "type": "IDQ_bounds_generator_sample"
    },
    {
      "base_term": 20,
      "id": "iqr_bounds-7d",
      "must_specify": [
        "coeff"
      ],
      "sample_size": 12,
      "type": "IDQ_bounds_generator_sample"
    },
    {
      "duration_ms": 300000,
      "id": "avg_rps",
      "max_sample_size": 50,
      "type": "avg_window"
    },
    {
      "default_state": "Ok",
      "id": "low_rps_muter",
      "must_specify": [
        "lower"
      ],
      "type": "state_transistor"
    },
    {
      "alert_text_template": "high timings = {value:.0f} ms, 1h median = {block_params__iqr_bounds__median:.0f} ms",
      "fixed_lower_bound": 0,
      "id": "oob",
      "type": "out_of_bounds_state",
      "yield_state_on_bounds_in": false
    },
    {
      "id": "schmitt",
      "lower_time_ms": 0,
      "type": "schmitt_state_window",
      "upper_time_ms": 210000
    },
    {
      "id": "peak_indicator",
      "sample_size": 5,
      "type": "peak_indicator"
    },
    {
      "default_state": "Ok",
      "id": "peak_muter",
      "type": "state_transistor",
      "upper": 0.5
    },
    {
      "default_state": "Ok",
      "fixed_lower": 0,
      "id": "7d_iqr_muter",
      "inverse": true,
      "type": "state_transistor",
      "upper": 0,
      "additional_meta": {
        "timings_type": "template"
      },
      "save_additional_meta_to_db": true
    }
  ],
  "entry_points": [
    {
      "id": "entry_timings",
      "type": "data_entry_point"
    },
    {
      "id": "entry_timings-7d",
      "type": "data_entry_point"
    },
    {
      "id": "entry_rps",
      "type": "data_entry_point"
    }
  ],
  "history_data_duration_sec": 3600,
  "name": "IQR, ignore low rps, detect peaks, check -7d ",
  "out_points": [
    {
      "debug": [
        "state"
      ],
      "id": "alert",
      "type": "state_out_point"
    }
  ],
  "type": "template",
  "wires": [
    {
      "from": "entry_timings",
      "to": "iqr_bounds",
      "type": "data"
    },
    {
      "from": "entry_timings",
      "to": "oob",
      "type": "data"
    },
    {
      "from": "iqr_bounds",
      "to": "oob",
      "type": "bounds"
    },
    {
      "from": "oob",
      "to": "schmitt",
      "type": "state"
    },
    {
      "from": "schmitt",
      "to": "low_rps_muter",
      "type": "state"
    },
    {
      "from": "entry_rps",
      "to": "avg_rps",
      "type": "data"
    },
    {
      "from": "avg_rps",
      "to": "low_rps_muter",
      "type": "data"
    },
    {
      "from": "entry_timings",
      "to": "peak_indicator",
      "type": "data"
    },
    {
      "from": "peak_indicator",
      "to": "peak_muter",
      "type": "data"
    },
    {
      "from": "low_rps_muter",
      "to": "peak_muter",
      "type": "state"
    },
    {
      "from": "peak_muter",
      "to": "7d_iqr_muter",
      "type": "state"
    },
    {
      "from": "entry_timings-7d",
      "to": "iqr_bounds-7d",
      "type": "data"
    },
    {
      "from": "iqr_bounds-7d",
      "to": "7d_iqr_muter",
      "type": "bounds"
    },
    {
      "from": "entry_timings",
      "to": "7d_iqr_muter",
      "type": "data"
    },
    {
      "from": "7d_iqr_muter",
      "to": "alert",
      "type": "state"
    }
  ]
}
$$::JSONB, 'template'),
('schema_timings-p95', 'schema p95', $$
{
  "name": "Timings p95",
  "params": {
    "7d_iqr_muter": {
      "additional_meta": {
        "timings_type": "p95"
      }
    },
    "iqr_bounds-7d": {
      "coeff": 2
    },
    "low_rps_muter": {
      "lower": 20
    }
  },
  "type": "schema",
  "use_template": "template_timings"
}
$$::JSONB, 'schema'),
('schema_timings-p98', 'schema p98', $$
{
  "name": "Timings p98",
  "params": {
    "7d_iqr_muter": {
      "additional_meta": {
        "timings_type": "p98"
      }
    },
    "iqr_bounds-7d": {
      "coeff": 3
    },
    "low_rps_muter": {
      "lower": 100
    }
  },
  "type": "schema",
  "use_template": "template_timings"
}
$$::JSONB, 'schema'),
('schema_experimental_aggregation', 'Schema to test aggregation', $$
{
  "blocks": [
    {
      "add_not_ok_to_meta": true,
      "aggregation_key": "host_name",
      "id": "cpu_aggregator",
      "save_not_ok_to_db": true,
      "skip_no_data": true,
      "type": "worst_state_aggregator",
      "additional_meta": {
        "check_type": "cpu"
      },
      "save_additional_meta_to_db": true
    },
    {
      "add_not_ok_to_meta": true,
      "aggregation_key": "timings_type",
      "id": "timings_aggregator",
      "save_not_ok_to_db": true,
      "skip_no_data": true,
      "type": "worst_state_aggregator",
      "additional_meta": {
        "check_type": "timings"
      },
      "save_additional_meta_to_db": true
    },
    {
      "add_not_ok_to_meta": true,
      "aggregation_key": "check_type",
      "id": "cpu_timings_aggregator",
      "save_not_ok_to_db": true,
      "skip_no_data": true,
      "type": "best_state_aggregator"
    }
  ],
  "entry_points": [
    {
      "id": "cpu_entry",
      "type": "state_entry_point"
    },
    {
      "id": "timings_entry",
      "type": "state_entry_point"
    }
  ],
  "history_data_duration_sec": 0,
  "name": "Experimental aggregation",
  "out_points": [
    {
      "id": "alert",
      "type": "state_out_point"
    }
  ],
  "wires": [
    {
      "from": "cpu_entry",
      "to": "cpu_aggregator",
      "type": "state"
    },
    {
      "from": "cpu_aggregator",
      "to": "cpu_timings_aggregator",
      "type": "state"
    },
    {
      "from": "timings_entry",
      "to": "timings_aggregator",
      "type": "state"
    },
    {
      "from": "timings_aggregator",
      "to": "cpu_timings_aggregator",
      "type": "state"
    },
    {
      "from": "cpu_timings_aggregator",
      "to": "alert",
      "type": "state"
    }
  ]
}
$$::JSONB, 'schema');

-- Service 139 with stable/prestable

insert into services (id, name, cluster_type, updated, deleted, project_id,
                      project_name, maintainers) values
    (139, 'test_service', 'nanny', now() at time zone 'utc', false, -1, 'test_project',
     '{}');

insert into branches (id, service_id, env, direct_link)
values (1391, 139, 'stable', 'test_branch_stable');
insert into branches (id, service_id, env, direct_link)
values (1392, 139, 'prestable', 'test_branch_prestable');

insert into branch_hosts (host_name, branch_id)
values ('host_name_1_stable', 1391);
insert into branch_hosts (host_name, branch_id)
values ('host_name_2_prestable', 1392);

insert into branch_domains (branch_id, solomon_object, name)
values (1391, 'test_solomon_object_yandex_net', 'test_domain_name_yandex_net');
insert into branch_domains (branch_id, solomon_object, name)
values (1391, 'test_solomon_object_yandex_net_v1_handler_GET', 'test-domain.yandex.net/v1/handler_GET');

-- Mod to disable cpu circuit for stable host

insert into spec_template_mods(id, spec_template_id, service_id, host_name, type, mod_data, apply_when)
values (1, 'rtc_cpu_usage', 139, 'host_name_1_stable', 'spec_disable', '{"disable": true}', 'always');
