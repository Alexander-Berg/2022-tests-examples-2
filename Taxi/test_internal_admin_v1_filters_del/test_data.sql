INSERT INTO signal_device_api.internal_filters (
    id,
    filter_name,
    filter_json,
    x_yandex_uid
)
VALUES 
(
    'id-1',
    'diveces',
    '{"name": "diveces", "conditions": [{"field": "declared_serial_numbers.hw_id", "comparison": "ge", "value": 1}], "conditions_operator": "and"}'::JSONB,
    '54591353'
),
(
    'id-2',
    'test',
    '{"name": "test", "conditions": [{"field": "declared_serial_numbers.hw_id", "comparison": "ne", "value": 3}], "conditions_operator": "and"}'::JSONB,
    '54591353'
),
(
    'id-3',
    'events',
    '{"name": "events", "conditions": [{"field": "declared_serial_numbers.hw_id", "comparison": "eq", "value": 2}], "conditions_operator": "and"}'::JSONB,
    '121766829'
);
