INSERT INTO fleet_reports_storage.operations (
    id,
    park_id,
    client_type,
    client_id,
    name,
    status,
    created_at,
    updated_at,
    file_name
)
VALUES (
    'base_operation_00000000000000002',
    'base_park_id_0',
    'driver_id',
    'base_driver_id_0',
    'report_vat_by_driver',
    'new',
    '2021-07-01T00:00:00+00:00',
    '2021-07-01T00:00:00+00:00',
    'March 2021'
),
(
    'base_operation_00000000000000003',
    'base_park_id_0',
    'driver_id',
    'base_driver_id_0',
    'report_vat_by_driver',
    'uploaded',
    '2021-07-02T10:35:00+00:00',
    '2021-07-02T10:35:00+00:00',
    'March 2021'
);
