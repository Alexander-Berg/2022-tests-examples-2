INSERT INTO reports
(
    uuid,
    brand_id,
    place_id,
    status,
    type,
    report_type,
    period,

    fail_reason,
    stacktrace,

    created_at,
    updated_at
)
VALUES
(
    'd9c3f450-203b-446a-b8d2-5b868061d5ff',
    'brand_id',
    NULL,
    'new',
    'sftp',
    'test_report_type',
    'daily',
    NULL,
    NULL,
    '2021-07-07 10:00:00',
    '2021-07-07 10:00:00'
)

;
