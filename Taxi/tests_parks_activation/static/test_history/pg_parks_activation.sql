INSERT INTO parks_activation.change_history (id, timestamp, park_id, field_name, before, after, additional_data)
VALUES
(3, '1970-01-15T06:58:08.001'::TIMESTAMPTZ, 'park2', 'deactivated', null, 'true', '{ "reason": "low balance", "threshold": 1.0 }'),
(1, '1970-01-15T06:56:08.000'::TIMESTAMPTZ, 'park1', 'field1', 'val1', 'val2', null),
(2, '1970-01-15T06:58:08.000'::TIMESTAMPTZ, 'park1', 'field1', 'val2', 'val1', null),
(4, '1970-01-15T06:58:09.001'::TIMESTAMPTZ, 'park1', 'deactivated', null, 'true', '{ "reason": "no active contracts" }'),
(5, '1970-01-15T06:58:10.001'::TIMESTAMPTZ, 'park2', 'deactivated', null, 'false', null);
