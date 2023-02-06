INSERT INTO eats_report_storage.order_history_reports (
    report_id,
    partner_id,
    yql_operation_id,
    yql_operation_status,
    filters,
    created_at,
    updated_at
)
VALUES
(
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    111,
    99,
    'running',
    '{"places": [55, 66], "from": "2017-01-29T20:03:59+03:00", "to": "2017-01-30T20:03:59+03:00", "statuses": ["new"], "delivery_types": ["native"]}'::JSONB,
    '2021-05-01 00:00:00'::timestamptz,
    '2021-05-02 00:00:00'::timestamptz
);
