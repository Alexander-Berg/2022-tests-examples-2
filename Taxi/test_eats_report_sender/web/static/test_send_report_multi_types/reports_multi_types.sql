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
    'uuid1',
    'brand_id',
    NULL,
    'success',
    'sftp',
    'test_report_type',
    'daily',
    NULL,
    NULL,
    '2021-07-07 10:00:00',
    '2021-07-07 10:00:00'
),
(
    'uuid1',
    'brand_id',
    NULL,
    'fail',
    'email',
    'test_report_type',
    'daily',
    NULL,
    NULL,
    '2021-07-07 10:00:00',
    '2021-07-07 10:00:00'
)

;
