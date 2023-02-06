insert into eats_performer_statistics.statistics (
    performer_id,
    metric_name,
    metric_interval,
    value,
    final_items_count,
    created_at,
    performer_timezone,
    utc_from,
    utc_to
)
values (
'1', 'fixed_shifts_work_hours_per_month', 'day', 11, 11, '2021-09-03T12:00:00.000000+03:00',
'Asia/Vladivostok',
'2021-09-01T00:00:00.000000+03:00', '2021-09-02T00:00:00.000000+03:00'
),
(
'1', 'fixed_shifts_work_hours_per_month', 'day', 12, 12, '2021-09-03T12:00:00.000000+03:00',
'Europe/Moscow',
'2021-09-01T10:00:00.000000+03:00', '2021-09-02T00:00:00.000000+03:00'
),
(
'1', 'fixed_shifts_work_hours_per_month', 'day', 13, 13, '2021-09-03T12:00:00.000000+03:00',
'Europe/Moscow',
'2021-09-01T00:00:00.000000+03:00', '2021-09-02T00:00:00.000000+03:00'
),
(
'1', 'fixed_shifts_work_days_per_month', 'day', 14, 14, '2021-09-03T12:00:00.000000+03:00',
'Europe/Moscow',
'2021-09-01T10:00:00.000000+03:00', '2021-09-02T00:00:00.000000+03:00'
),
(
'1', 'fixed_shifts_work_days_per_month', 'day', 15, 15, '2021-09-03T12:00:00.000000+03:00',
'Europe/Moscow',
'2021-09-01T00:00:00.000000+03:00', '2021-09-02T00:00:00.000000+03:00'
),
(
'1', 'fixed_shifts_work_days_per_month', 'day', 16, 16, '2021-09-03T12:00:00.000000+03:00',
'Europe/Moscow',
'2021-09-01T00:00:00.000000+03:00', '2021-09-02T00:00:00.000000+03:00'
),
(
'1', 'fixed_shifts_work_days_per_month', 'day', 17, 17, '2021-09-03T12:00:00.000000+03:00',
'Europe/Moscow',
'2021-09-01T00:00:00.000000+03:00', '2021-09-02T00:00:00.000000+03:00'
),
('2', 'delivery_rate', 'day', 21, 21, '2021-09-03T12:00:00.000000+03:00',
'Europe/Moscow',
'2021-09-01T00:00:00.000000+03:00', '2021-09-02T00:00:00.000000+03:00'
);
