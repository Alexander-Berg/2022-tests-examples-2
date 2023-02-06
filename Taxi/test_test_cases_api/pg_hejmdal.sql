insert into circuit_schemas (id, type, description, circuit_schema, updated) values
(
    'schema_test', 'schema',
    'Schema for testing of hejmdal in testsuite',$$
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
    $$::JSONB, '1970-01-15T06:58:08.001+00:00'::TIMESTAMPTZ),
(
    'schema_test_2', 'schema',
    'Schema 2 for testing of hejmdal in testsuite',$$
    {
      "name": "schema_test 2",
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
    $$::JSONB, '1970-01-15T06:58:08.001+00:00'::TIMESTAMPTZ),
(
    'template_test', 'template',
    'Template for testing of hejmdal in testsuite',$$
    {
      "name": "template_test",
      "type": "template",
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

insert into test_cases (description, test_data_id, schema_id, out_point_id, start_time, end_time, check_type)
values ('test_case_description', '3', 'schema_test_2', 'alert1',
        '1970-01-15T06:58:08.001+00:00'::TIMESTAMPTZ,
        '1970-01-15T06:58:08.001+00:00'::TIMESTAMPTZ,
        'has_alert')

