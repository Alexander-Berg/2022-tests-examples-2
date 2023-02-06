INSERT INTO dispatch_settings.groups (name, description) VALUES ('old', 'description');

INSERT INTO dispatch_settings.parameters (field_name, schema)
VALUES
(
    'INTEGER_POSITIVE_FIELD',
    '{"type": "integer", "minimum": 0}'
),
(
    'NEW_INTEGER_FIELD',
    '{"type": "integer"}'
);
