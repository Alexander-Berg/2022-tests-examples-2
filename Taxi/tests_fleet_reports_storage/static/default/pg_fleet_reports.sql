INSERT INTO fleet_reports_storage.operations (
    id,
    park_id,
    client_type,
    client_id,
    name,
    status,
    file_name,
    locale,
    created_at,
    updated_at,
    deleted_at,
    uploaded_at
)
VALUES (
    'base_operation_00000000000000000',
    'base_park_id_0',
    'yandex_user',
    '0',
    'report_orders',
    'new',
    'report_orders.csv',
    'ru',
    '2019-01-01T00:00:00+00:00',
    '2019-01-01T00:00:00+00:00',
    null,
    null
),
(
    'base_operation_00000000000000001',
    'base_park_id_0',
    'yandex_user',
    '0',
    'report_orders',
    'uploaded',
    'report_orders.csv',
    'ru',
    '2019-01-01T00:00:00+00:00',
    '2019-01-01T00:00:00+00:00',
    null,
    '2019-01-01T00:00:00+00:00'
),
(
    'base_operation_00000000000000002',
    'base_park_id_0',
    'yandex_user',
    '0',
    'report_orders',
    'deleted',
    'report_orders.csv',
    'ru',
    '2019-01-01T00:00:00+00:00',
    '2019-01-02T00:00:00+00:00',
    '2019-01-02T00:00:00+00:00',
    '2019-01-02T00:00:00+00:00'
);