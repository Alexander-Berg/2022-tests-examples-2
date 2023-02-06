INSERT INTO signal_device_api.internal_filters (
    filter_name,
    filter_json,
    x_yandex_uid
)
VALUES (
    'diveces',
    '{"name": "diveces", "conditions": [{"field": "declared_serial_numbers.hw_id", "comparison": "ge", "value": 1}], "conditions_operator": "and"}'::JSONB,
    '54591353'
);
