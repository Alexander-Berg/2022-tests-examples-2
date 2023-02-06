INSERT INTO accountant_reports
(
    uuid,
    balance_internal_id,
    status,
    type,
    period,
    report_date,
    file_link,

    fail_reason,
    stacktrace,

    created_at,
    updated_at
)
VALUES
(
    '1',
    1,
    'new',
    'email',
    'weekly',
    '2022-07-01 00:00:00',
    'accountant_report/report.xlsx',
    NULL,
    NULL,
    '2021-07-07 10:00:00',
    '2021-07-07 10:00:00'
)

;
