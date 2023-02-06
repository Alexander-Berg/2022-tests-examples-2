insert into circuit_schemas
    (id, description, circuit_schema, updated)
values
('schema_ks_test', 'KS test', $$
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
$$::JSONB, '1970-01-15T07:58:08.001+00:00'::TIMESTAMPTZ);

insert into test_data
    (description, schema_id, start_time, precedent_time, end_time,
     data, meta)
values
(
 'test description',
 'schema_id',
 '2019-11-27T11:20:00.001+00:00'::TIMESTAMPTZ,
 '2019-11-27T11:29:00.001+00:00'::TIMESTAMPTZ,
 '2019-11-27T11:39:00.001+00:00'::TIMESTAMPTZ,
 $$
 [
   {
     "entry_point_id": "entry_1",
     "timeseries": {
       "timestamps": [
         1574853600000,
         1574853660000,
         1574853720000,
         1574853780000,
         1574853840000,
         1574853900000,
         1574853960000,
         1574854020000,
         1574854080000,
         1574854140000,
         1574854200000,
         1574854260000,
         1574854320000,
         1574854380000,
         1574854440000,
         1574854500000,
         1574854560000,
         1574854620000,
         1574854680000,
         1574854740000
       ],
       "values": [
         10.0,
         18.0,
         50.0,
         4.0,
         7.0,
         21.0,
         17.0,
         9.0,
         4.0,
         4.0,
         7.0,
         11.0,
         9.0,
         11.0,
         4.0,
         6.0,
         5.0,
         11.0,
         10.0,
         17.0
       ]
     }
   },
   {
     "entry_point_id": "entry_2",
     "timeseries": {
       "timestamps": [
         1574853600000,
         1574853660000,
         1574853720000,
         1574853780000,
         1574853840000,
         1574853900000,
         1574853960000,
         1574854020000,
         1574854080000,
         1574854140000,
         1574854200000,
         1574854260000,
         1574854320000,
         1574854380000,
         1574854440000,
         1574854500000,
         1574854560000,
         1574854620000,
         1574854680000,
         1574854740000
       ],
       "values": [
         50.0,
         50.0,
         50.0,
         50.0,
         50.0,
         50.0,
         50.0,
         50.0,
         50.0,
         50.0,
         50.0,
         50.0,
         50.0,
         50.0,
         50.0,
         50.0,
         50.0,
         50.0,
         50.0,
         50.0
       ]
     }
   }
 ]$$::JSONB, $${}$$::JSONB);
