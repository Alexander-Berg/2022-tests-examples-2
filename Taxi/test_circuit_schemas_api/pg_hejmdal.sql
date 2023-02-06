insert into circuit_schemas (id, type, description, circuit_schema, updated) values
(
'schema_rtc_cpu_usage_v2', 'schema', 'RTC cpu usage',$$
{
  "name": "RTC CPU usage",
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
      "id": "alert",
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
      "type": "data_entry_point",
      "debug": [
        "data"
      ]
    },
    {
      "id": "usage",
      "type": "data_entry_point"
    }
  ],
  "history_data_duration_sec": 900
}
$$::JSONB, '1970-01-15T06:58:08.001+00:00'::TIMESTAMPTZ),
('schema_rtc_memory_usage_v2', 'schema', 'RTC memory usage',$$
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
('schema_ks_test', 'schema', 'KS test', $$
{
  "type": "schema",
  "blocks": [
    {
      "debug": ["data"],
      "double_check": true,
      "id": "ks_test",
      "lag_ms": 86400000,
      "max_sample_size": 360,
      "max_samples": 1000,
      "min_samples": 5,
      "type": "ks_test",
      "window_ms": 3600000
    },
    {
      "debug": ["bounds"],
      "id": "p_value_bound",
      "lower": 1e-08,
      "type": "static_bounds_generator",
      "upper": 2.0
    },
    {
      "debug": ["state"],
      "id": "low_p_value_alert",
      "type": "out_of_bounds_state",
      "yield_state_on_bounds_in": false
    }
  ],
  "entry_points": [
    {
      "id": "entry_data",
      "type": "data_entry_point"
    }
  ],
  "name": "KS test",
  "out_points": [
    {
      "id": "alert",
      "type": "bypass"
    }
  ],
  "wires": [
    {
      "from": "p_value_bound",
      "to": "low_p_value_alert",
      "type": "bounds"
    },
    {
      "from": "entry_data",
      "to": "ks_test",
      "type": "data"
    },
    {
      "from": "ks_test",
      "to": "low_p_value_alert",
      "type": "data"
    },
    {
      "from": "low_p_value_alert",
      "to": "alert",
      "type": "state"
    }
  ]
}
$$::JSONB, '1970-01-15T07:58:08.001+00:00'::TIMESTAMPTZ),
('schema_timings-p95', 'schema', 'Inter-quartile range + anti-flap + mute low rps + mute -7d iqr', $$
{
  "name": "IQR, ignore low rps, detect peaks, check -7d",
  "type": "schema",
  "wires": [
    {
      "to": "iqr_bounds",
      "from": "entry_timings",
      "type": "data"
    },
    {
      "to": "oob",
      "from": "entry_timings",
      "type": "data"
    },
    {
      "to": "oob",
      "from": "iqr_bounds",
      "type": "bounds"
    },
    {
      "to": "schmitt",
      "from": "oob",
      "type": "state"
    },
    {
      "to": "low_rps_muter",
      "from": "schmitt",
      "type": "state"
    },
    {
      "to": "low_rps_muter",
      "from": "entry_rps",
      "type": "data"
    },
    {
      "to": "peak_indicator",
      "from": "entry_timings",
      "type": "data"
    },
    {
      "to": "peak_muter",
      "from": "peak_indicator",
      "type": "data"
    },
    {
      "to": "peak_muter",
      "from": "low_rps_muter",
      "type": "state"
    },
    {
      "to": "7d_iqr_muter",
      "from": "peak_muter",
      "type": "state"
    },
    {
      "to": "iqr_bounds-7d",
      "from": "entry_timings-7d",
      "type": "data"
    },
    {
      "to": "7d_iqr_muter",
      "from": "iqr_bounds-7d",
      "type": "bounds"
    },
    {
      "to": "7d_iqr_muter",
      "from": "entry_timings",
      "type": "data"
    },
    {
      "to": "alert",
      "from": "7d_iqr_muter",
      "type": "state"
    }
  ],
  "blocks": [
    {
      "id": "iqr_bounds",
      "type": "IDQ_bounds_generator_sample",
      "coeff": 3,
      "base_term": 10,
      "sample_size": 60
    },
    {
      "id": "iqr_bounds-7d",
      "type": "IDQ_bounds_generator_sample",
      "coeff": 1.1,
      "base_term": 10,
      "sample_size": 12
    },
    {
      "id": "low_rps_muter",
      "type": "state_transistor",
      "debug": true,
      "lower": 10,
      "default_state": "Ok"
    },
    {
      "id": "oob",
      "type": "out_of_bounds_state",
      "debug": true,
      "fixed_lower_bound": 0,
      "yield_state_on_bounds_in": false
    },
    {
      "id": "schmitt",
      "type": "schmitt_state_window",
      "debug": true,
      "lower_time_ms": 0,
      "upper_time_ms": 210000
    },
    {
      "id": "peak_indicator",
      "type": "peak_indicator",
      "debug": true,
      "sample_size": 5
    },
    {
      "id": "peak_muter",
      "type": "state_transistor",
      "debug": true,
      "upper": 0.5,
      "default_state": "Ok"
    },
    {
      "id": "7d_iqr_muter",
      "type": "state_transistor",
      "upper": 0.0,
      "fixed_lower": 0.0,
      "inverse": true,
      "default_state": "Ok"
    }
  ],
  "out_points": [
    {
      "id": "alert",
      "type": "bypass"
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
  "history_data_duration_sec": 3600
}
$$::JSONB, '1970-01-15T08:58:08.001+00:00'::TIMESTAMPTZ),
('schema_timings-p98', 'schema', 'Inter-quartile range + anti-flap + mute low rps + mute -7d iqr', $$
{
  "name": "IQR, ignore low rps, detect peaks, check -7d",
  "type": "schema",
  "wires": [
    {
      "to": "iqr_bounds",
      "from": "entry_timings",
      "type": "data"
    },
    {
      "to": "oob",
      "from": "entry_timings",
      "type": "data"
    },
    {
      "to": "oob",
      "from": "iqr_bounds",
      "type": "bounds"
    },
    {
      "to": "schmitt",
      "from": "oob",
      "type": "state"
    },
    {
      "to": "low_rps_muter",
      "from": "schmitt",
      "type": "state"
    },
    {
      "to": "low_rps_muter",
      "from": "entry_rps",
      "type": "data"
    },
    {
      "to": "peak_indicator",
      "from": "entry_timings",
      "type": "data"
    },
    {
      "to": "peak_muter",
      "from": "peak_indicator",
      "type": "data"
    },
    {
      "to": "peak_muter",
      "from": "low_rps_muter",
      "type": "state"
    },
    {
      "to": "7d_iqr_muter",
      "from": "peak_muter",
      "type": "state"
    },
    {
      "to": "iqr_bounds-7d",
      "from": "entry_timings-7d",
      "type": "data"
    },
    {
      "to": "7d_iqr_muter",
      "from": "iqr_bounds-7d",
      "type": "bounds"
    },
    {
      "to": "7d_iqr_muter",
      "from": "entry_timings",
      "type": "data"
    },
    {
      "to": "alert",
      "from": "7d_iqr_muter",
      "type": "state"
    }
  ],
  "blocks": [
    {
      "id": "iqr_bounds",
      "type": "IDQ_bounds_generator_sample",
      "coeff": 3,
      "base_term": 10,
      "sample_size": 60
    },
    {
      "id": "iqr_bounds-7d",
      "type": "IDQ_bounds_generator_sample",
      "coeff": 1.1,
      "base_term": 10,
      "sample_size": 12
    },
    {
      "id": "low_rps_muter",
      "type": "state_transistor",
      "lower": 100,
      "default_state": "Ok"
    },
    {
      "id": "oob",
      "type": "out_of_bounds_state",
      "fixed_lower_bound": 0,
      "yield_state_on_bounds_in": false
    },
    {
      "id": "schmitt",
      "type": "schmitt_state_window",
      "lower_time_ms": 0,
      "upper_time_ms": 210000
    },
    {
      "id": "peak_indicator",
      "type": "peak_indicator",
      "sample_size": 5
    },
    {
      "id": "peak_muter",
      "type": "state_transistor",
      "upper": 0.5,
      "default_state": "Ok"
    },
    {
      "id": "7d_iqr_muter",
      "type": "state_transistor",
      "upper": 0.0,
      "fixed_lower": 0.0,
      "inverse": true,
      "default_state": "Ok"
    }
  ],
  "out_points": [
    {
      "id": "alert",
      "type": "bypass"
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
  "history_data_duration_sec": 3600
}$$::JSONB, '1970-01-15T08:58:08.001+00:00'::TIMESTAMPTZ),
('schema_oom_check', 'schema', 'Check oom indicator, crit on > 0.9', $$
{
  "type": "schema",
  "blocks": [
    {
      "id": "oom_indicator_bound",
      "lower": -1,
      "type": "static_bounds_generator",
      "upper": 0.9
    },
    {
      "id": "oom_oob",
      "emergency_state": "Critical",
      "type": "out_of_bounds_state"
    }
  ],
  "entry_points": [
    {
      "id": "entry_oom",
      "type": "data_entry_point"
    }
  ],
  "name": "OOM check",
  "out_points": [
    {
      "id": "alert",
      "type": "bypass"
    }
  ],
  "wires": [
    {
      "from": "entry_oom",
      "to": "oom_oob",
      "type": "data"
    },
    {
      "from": "oom_indicator_bound",
      "to": "oom_oob",
      "type": "bounds"
    },
    {
      "from": "oom_oob",
      "to": "alert",
      "type": "state"
    }
  ]
}
$$, '1970-01-15T08:58:08.001+00:00'::TIMESTAMPTZ),
('schema_test_delete', 'schema', 'Schema to test deletion', $$
{
  "blocks": [
    {
      "id": "oob",
      "type": "out_of_bounds_state"
    }
  ],
  "entry_points": [
  ],
  "name": "Test schema",
  "type": "schema",
  "out_points": [
    {
      "debug": true,
      "id": "state_out",
      "type": "bypass"
    }
  ],
  "wires": [
    {
      "from": "oob",
      "to": "state_out",
      "type": "state"
    }
  ]
}
$$, '1970-01-15T08:58:08.001+00:00'::TIMESTAMPTZ),
('schema_test', 'schema', 'test', $$
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
$$::JSONB, '1970-01-15T06:58:08.001+00:00'::TIMESTAMPTZ),
('schema_with_test_case', 'schema', 'test_schema_update_with_tests',$$
{
  "name": "test_name",
  "type": "schema",
  "history_data_duration_sec": 10,
  "entry_points": [{"id": "entry", "type": "data_entry_point"}],
  "out_points": [{"id": "alert", "type": "state_out_point"}],
  "blocks": [
    {
      "id": "no_data_block",
      "type": "no_data_state",
      "no_data_duration_before_warn_sec": 60,
      "no_data_duration_before_crit_sec": 120,
      "start_state": "Ok"
    }
  ],
  "wires": [
    {"to": "no_data_block", "from": "entry", "type": "state"},
    {"to": "alert", "from": "no_data_block", "type": "state"}
  ]
}$$::JSONB, '1970-01-15T06:58:08.001+00:00'::TIMESTAMPTZ);

insert into test_data
(test_id, description, schema_id, start_time, precedent_time,
 end_time, data, meta)
values
(1, 'test_schema_update_with_tests', 'schema_with_test_case',
 '2020-10-02 12:00:00.000000'::TIMESTAMPTZ,
 '2020-10-02 12:02:30.000000'::TIMESTAMPTZ,
 '2020-10-02 12:05:00.000000'::TIMESTAMPTZ,
 $$[
   {
     "timeseries": {
       "values": [1, 1, 1, 1],
       "timestamps": [
         1601640000000,
         1601640180000,
         1601640270000,
         1601640300000
       ]
     },
     "entry_point_id": "entry"
   }]$$::JSONB, $${}$$::JSON);

insert into test_cases
    (description, test_data_id, schema_id, out_point_id, start_time, end_time, check_type, is_enabled)
values ('test_schema_update_with_tests - success',
        '1',
        'schema_with_test_case',
        'alert',
        '2020-10-02 12:00:00.000000'::TIMESTAMPTZ,
        '2020-10-02 12:05:00.000000'::TIMESTAMPTZ,
        'has_alert', true),
       ('test_schema_update_with_tests - should fail',
        '1',
        'schema_with_test_case',
        'alert',
        '2020-10-02 12:00:00.000000'::TIMESTAMPTZ,
        '2020-10-02 12:00:55.000000'::TIMESTAMPTZ,
        'has_alert', false)
