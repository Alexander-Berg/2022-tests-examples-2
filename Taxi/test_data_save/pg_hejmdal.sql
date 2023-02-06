insert into circuit_schemas (id, description, circuit_schema, updated) values
(
    'schema_test', 'Schema for testing of hejmdal in testsuite',$$
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
$$::JSONB, '1970-01-15T06:58:08.001+00:00'::TIMESTAMPTZ);
