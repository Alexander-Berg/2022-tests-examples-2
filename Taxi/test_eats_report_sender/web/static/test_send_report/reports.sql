insert into reports
(
    uuid,
    brand_id,
    place_id,
    status,
    type,
    report_type,
    period,
    created_at,
    updated_at
)
values
(
    'uuid1',
    'brand_id2',
    null,
    'in_progress',
    'sftp',
    'test_report_type',
    'daily',
    '2021-06-24 00:00:00',
    '2021-06-24 00:00:00'
)
;
