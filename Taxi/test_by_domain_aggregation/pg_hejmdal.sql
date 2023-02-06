insert into circuit_schemas (id, description, circuit_schema, type, updated) values
('template_domains_aggregation', '',$$
 {
   "blocks": [
     {
       "add_not_ok_to_meta": true,
       "aggregation_key": "domain",
       "bypass_keys": [
         "description_info"
       ],
       "id": "domains_aggregator",
       "save_additional_meta_to_db": true,
       "save_not_ok_to_db": true,
       "skip_no_data": true,
       "type": "worst_state_aggregator"
     },
     {
       "aggregation_object_type": "object",
       "aggregator_id": "domains_aggregator",
       "id": "meta_formatter",
       "keys_in_aggregator_object": [
         "name",
         "dorblu_object",
         "description_info"
       ],
       "meta_keys": [
         "domains_list",
         "dorblu_objects_list",
         "descriptions_list"
       ],
       "type": "aggregation_meta_formatter"
     },
     {
       "id": "description_prioritizer",
       "array_key": "descriptions_list",
       "priority_key": "priority",
       "description_key": "description",
       "type": "description_prioritizer"
     }
   ],
   "entry_points": [
     {
       "id": "entry",
       "meta_override_keys": [
         "circuit_id",
         "juggler_service_name",
         "yandex_monitoring_dashboard_link"
       ],
       "type": "state_connection_point"
     }
   ],
   "history_data_duration_sec": 0,
   "name": "Aggregate of by-domain checks",
   "out_points": [
     {
       "id": "alert",
       "type": "state_out_point"
     }
   ],
   "type": "template",
   "wires": [
     {
       "from": "entry",
       "to": "domains_aggregator",
       "type": "state"
     },
     {
       "from": "domains_aggregator",
       "to": "meta_formatter",
       "type": "state"
     },
     {
       "from": "meta_formatter",
       "to": "description_prioritizer",
       "type": "state"
     },
     {
       "from": "description_prioritizer",
       "to": "alert",
       "type": "state"
     }
   ]
 }
$$::JSONB, 'template', '1970-01-15T06:58:08.001+00:00'::TIMESTAMPTZ),
('schema_bad_rps_aggregation', 'High bad RPS.',$$
 {
   "name": "High bad rps.",
   "params": {},
   "type": "schema",
   "use_template": "template_domains_aggregation"
 }
$$::JSONB, 'schema', '1970-01-15T06:58:08.001+00:00'::TIMESTAMPTZ),
('schema_ok_rps_aggregation', 'High ok RPS deviation.',$$
 {
   "name": "High ok rps deviation.",
   "params": {},
   "type": "schema",
   "use_template": "template_domains_aggregation"
 }
$$::JSONB, 'schema', '1970-01-15T06:58:08.001+00:00'::TIMESTAMPTZ),
('schema_timings-p95_aggregation', 'High timings (p95).',$$
 {
   "name": "High timings (p95).",
   "params": {},
   "type": "schema",
   "use_template": "template_domains_aggregation"
 }
$$::JSONB, 'schema', '1970-01-15T06:58:08.001+00:00'::TIMESTAMPTZ),
('schema_500_rps_low_aggregation', 'High 500 rps for low rps.',$$
 {
   "name": "High 500 rps for low rps.",
   "params": {},
   "type": "schema",
   "use_template": "template_domains_aggregation"
 }
$$::JSONB, 'schema', '1970-01-15T06:58:08.001+00:00'::TIMESTAMPTZ),
('schema_timings-p98_aggregation', 'High timings (p98).',$$
 {
   "name": "High timings (p98).",
   "params": {},
   "type": "schema",
   "use_template": "template_domains_aggregation"
 }
$$::JSONB, 'schema', '1970-01-15T06:58:08.001+00:00'::TIMESTAMPTZ),
('schema_bad_rps', 'Bad RPS',$$
 {
   "blocks": [
     {
       "id": "priority_filler",
       "path": [
         "domain",
         "description_info",
         "priority"
       ],
       "type": "meta_filler"
     },
     {
       "id": "description_filler",
       "path": [
         "domain",
         "description_info",
         "description"
       ],
       "type": "meta_filler"
     },
     {
       "id": "data_to_bounds",
       "lower_coeff": 0,
       "type": "data_to_bounds",
       "upper_base_term": 10,
       "upper_coeff": 3
     },
     {
       "alert_text_template": "high bad rps = {value:.0f}",
       "emergency_state": "Warning",
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
       "default_state": "Ok",
       "id": "low_rps_muter",
       "lower": 10,
       "type": "state_transistor"
     },
     {
       "default_state": "Ok",
       "id": "high_bad_rps_muter",
       "type": "state_transistor",
       "upper": 0.07
     }
   ],
   "entry_points": [
     {
       "id": "entry_rps",
       "type": "data_entry_point"
     },
     {
       "id": "entry_bad_rps",
       "type": "data_entry_point"
     },
     {
       "id": "entry_bad_rps_bound",
       "type": "data_entry_point"
     },
     {
       "id": "entry_bad_rps_fraction_day",
       "type": "data_entry_point"
     }
   ],
   "history_data_duration_sec": 3600,
   "name": "Bad RPS",
   "out_points": [
     {
       "debug": [
         "state"
       ],
       "id": "alert",
       "type": "state_out_point"
     }
   ],
   "type": "schema",
   "wires": [
     {
       "from": "entry_rps",
       "to": "low_rps_muter",
       "type": "data"
     },
     {
       "from": "low_rps_muter",
       "to": "high_bad_rps_muter",
       "type": "state"
     },
     {
       "from": "high_bad_rps_muter",
       "to": "description_filler",
       "type": "state"
     },
     {
       "from": "description_filler",
       "to": "alert",
       "type": "state"
     },
     {
       "from": "entry_bad_rps_bound",
       "to": "data_to_bounds",
       "type": "data"
     },
     {
       "from": "data_to_bounds",
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
       "from": "entry_bad_rps",
       "to": "priority_filler",
       "type": "data"
     },
     {
       "from": "priority_filler",
       "to": "oob",
       "type": "data"
     },
     {
       "from": "entry_bad_rps_fraction_day",
       "to": "high_bad_rps_muter",
       "type": "data"
     }
   ]
 }
$$::JSONB, 'schema', '1970-01-15T06:58:08.001+00:00'::TIMESTAMPTZ),
('schema_ok_rps', 'dsc', $$
 {
   "blocks": [
     {
       "id": "priority_filler",
       "path": [
         "domain",
         "description_info",
         "priority"
       ],
       "type": "meta_filler"
     },
     {
       "id": "description_filler",
       "path": [
         "domain",
         "description_info",
         "description"
       ],
       "type": "meta_filler"
     },
     {
       "alert_text_template": "ok_rps deviation {value_percent:.0f}%",
       "fixed_lower_bound": -1,
       "fixed_upper_bound": 0.2,
       "id": "oob",
       "type": "out_of_bounds_state",
       "yield_state_on_bounds_in": false
     },
     {
       "id": "schmitt",
       "lower_time_ms": 0,
       "type": "schmitt_state_window",
       "upper_time_ms": 120000
     },
     {
       "default_state": "Ok",
       "id": "low_rps_muter",
       "lower": 10,
       "type": "state_transistor"
     }
   ],
   "description": "ok rps deviation",
   "entry_points": [
     {
       "id": "entry_ok_rps",
       "type": "data_entry_point"
     },
     {
       "id": "entry_ok_rps_deviation",
       "type": "data_entry_point"
     }
   ],
   "history_data_duration_sec": 120,
   "name": "Ok RPS deviation",
   "out_points": [
     {
       "id": "alert",
       "type": "state_out_point"
     }
   ],
   "type": "schema",
   "wires": [
     {
       "from": "entry_ok_rps_deviation",
       "to": "priority_filler",
       "type": "data"
     },
     {
       "from": "priority_filler",
       "to": "oob",
       "type": "data"
     },
     {
       "from": "oob",
       "to": "low_rps_muter",
       "type": "state"
     },
     {
       "from": "low_rps_muter",
       "to": "schmitt",
       "type": "state"
     },
     {
       "from": "schmitt",
       "to": "description_filler",
       "type": "state"
     },
     {
       "from": "description_filler",
       "to": "alert",
       "type": "state"
     },
     {
       "from": "entry_ok_rps",
       "to": "low_rps_muter",
       "type": "data"
     }
   ]
 }
$$::JSONB, 'schema', '1970-01-15T06:58:08.001+00:00'::TIMESTAMPTZ),
('schema_500_rps_low', 'dsc', $$
 {
   "blocks": [
     {
       "id": "priority_filler",
       "path": [
         "domain",
         "description_info",
         "priority"
       ],
       "type": "meta_filler"
     },
     {
       "id": "description_filler",
       "path": [
         "domain",
         "description_info",
         "description"
       ],
       "type": "meta_filler"
     },
     {
       "duration_ms": 300000,
       "id": "sum_ok_rps",
       "max_sample_size": 1000,
       "type": "sum_window"
     },
     {
       "duration_ms": 300000,
       "id": "sum_error_rps",
       "max_sample_size": 1000,
       "type": "sum_window"
     },
     {
       "alert_text_template": "high 500 rps = {value:.4f}",
       "emergency_state": "Warning",
       "fixed_lower_bound": -1,
       "fixed_upper_bound": 0.16,
       "id": "oob",
       "type": "out_of_bounds_state",
       "yield_state_on_bounds_in": false
     },
     {
       "default_state": "Ok",
       "id": "high_ok_rps_muter",
       "type": "state_transistor",
       "upper": 0.00001
     },
     {
       "default_state": "Ok",
       "id": "high_all_rps_muter",
       "type": "state_transistor",
       "upper": 1
     }
   ],
   "entry_points": [
     {
       "id": "entry_all_rps",
       "type": "data_entry_point"
     },
     {
       "id": "entry_error_rps",
       "type": "data_entry_point"
     },
     {
       "id": "entry_ok_rps",
       "type": "data_entry_point"
     }
   ],
   "history_data_duration_sec": 3600,
   "name": "Bad RPS",
   "out_points": [
     {
       "debug": [
         "state"
       ],
       "id": "alert",
       "type": "state_out_point"
     }
   ],
   "type": "schema",
   "wires": [
     {
       "from": "entry_ok_rps",
       "to": "sum_ok_rps",
       "type": "data"
     },
     {
       "from": "sum_ok_rps",
       "to": "high_ok_rps_muter",
       "type": "data"
     },
     {
       "from": "high_ok_rps_muter",
       "to": "high_all_rps_muter",
       "type": "state"
     },
     {
       "from": "high_all_rps_muter",
       "to": "description_filler",
       "type": "state"
     },
     {
       "from": "description_filler",
       "to": "alert",
       "type": "state"
     },
     {
       "from": "entry_error_rps",
       "to": "sum_error_rps",
       "type": "data"
     },
     {
       "from": "sum_error_rps",
       "to": "priority_filler",
       "type": "data"
     },
     {
       "from": "priority_filler",
       "to": "oob",
       "type": "data"
     },
     {
       "from": "oob",
       "to": "high_ok_rps_muter",
       "type": "state"
     },
     {
       "from": "entry_all_rps",
       "to": "high_all_rps_muter",
       "type": "data"
     }
   ]
 }
$$::JSONB, 'schema', '1970-01-15T06:58:08.001+00:00'::TIMESTAMPTZ),
('template_timings', 'dsc',$$
 {
   "blocks": [
     {
       "id": "priority_filler",
       "path": [
         "domain",
         "description_info",
         "priority"
       ],
       "type": "meta_filler"
     },
     {
       "id": "description_filler",
       "path": [
         "domain",
         "description_info",
         "description"
       ],
       "type": "meta_filler"
     },
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
       "upper": 0
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
       "additional_meta": {
         "timings_type": "template"
       },
       "debug": [
         "state"
       ],
       "id": "alert",
       "save_additinal_meta_to_db": true,
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
       "to": "priority_filler",
       "type": "data"
     },
     {
       "from": "priority_filler",
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
       "to": "description_filler",
       "type": "state"
     },
     {
       "from": "description_filler",
       "to": "alert",
       "type": "state"
     }
   ]
 }
$$::JSONB, 'template', '1970-01-15T06:58:08.001+00:00'::TIMESTAMPTZ),
('schema_timings-p95', 'dsc', $$
 {
   "name": "Timings p95",
   "params": {
     "alert": {
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
$$::JSONB, 'schema', '1970-01-15T06:58:08.001+00:00'::TIMESTAMPTZ),
('schema_timings-p98', 'dsc',$$
 {
   "name": "Timings p98",
   "params": {
      "alert": {
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
$$::JSONB, 'schema', '1970-01-15T06:58:08.001+00:00'::TIMESTAMPTZ);

insert into services (id, name, cluster_type) values
(139, 'hejmdal', 'nanny');

insert into branches (id, service_id, env, direct_link) values
(1, 139, 'stable', 'hejmdal_dirlink');

insert into branch_domains (branch_id, solomon_object, name) values
(1, 'hejmdal_yandex_net', 'hejmdal.yandex.net'),
(1, 'hejmdal_yandex_net_view_POST', 'hejmdal.yandex.net/view_POST'),
(1, 'hejmdal_yandex_net_view2_GET', 'hejmdal.yandex.net/view2_GET');

insert into spec_template_mods (id, spec_template_id, service_id, env, domain_name, type, mod_data) values
(1, 'bad_rps', 139, 'any', 'hejmdal.yandex.net/view_POST', 'spec_disable', '{"disable": false}'::JSONB),
(2, 'bad_rps', 139, 'any', 'hejmdal.yandex.net/view2_GET', 'spec_disable', '{"disable": false}'::JSONB),
(3, 'ok_rps', 139, 'any', 'hejmdal.yandex.net/view2_GET', 'spec_disable', '{"disable": false}'::JSONB),
(4, '500_rps_low', 139, 'any', 'hejmdal.yandex.net/view_POST', 'spec_disable', '{"disable": false}'::JSONB);
