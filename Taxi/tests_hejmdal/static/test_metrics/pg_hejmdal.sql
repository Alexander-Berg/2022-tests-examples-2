insert into circuit_schemas (id, description, circuit_schema, updated) values
('schema_test', 'Test schema', $$
{
  "blocks": [
    {
      "id": "oob",
      "type": "out_of_bounds_state"
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
  "name": "Test schema",
  "type": "schema",
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
  "wires": [
    {
      "from": "entry1",
      "to": "oob",
      "type": "data"
    },
    {
      "from": "oob",
      "to": "alert1",
      "type": "state"
    }
  ],
  "history_data_duration_sec": 0
}
$$, '1970-01-15T08:58:08.001+00:00'::TIMESTAMPTZ);
