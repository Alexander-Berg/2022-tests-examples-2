INSERT INTO json_table (id, created_at, json_type, jsonb_type)
VALUES
(
    'id_1',
    '2019-01-24T11:00:00',
    '{"a": "b"}',
    '{"foo": "bar"}'
),
(
    'id_2',
    '2019-01-24T11:00:00',
    '{"a2": "b2"}'::JSON,
    '{"foo2": "bar2"}'::JSONB
),
(
    'id_3_null',
    '2019-01-24T11:00:00',
    'null'::JSON,
    'null'::JSONB
),
(
    'id_4_null',
    '2019-01-24T11:00:00',
    null,
    null
);

INSERT INTO simple_table (id) VALUES (111);
