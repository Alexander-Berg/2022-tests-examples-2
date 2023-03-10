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
'1', 'delivery_rate', 'day', 11.1, 11, '2021-06-21T00:00:00.000000+10:00',
'Asia/Vladivostok',
'2021-06-20T00:00:00.000000+10:00', '2021-06-21T00:00:00.000000+10:00'
),
(
'1', 'delivery_rate', 'day', 12.1, 12, '2021-06-21T23:59:59.999999+10:00',
'Asia/Vladivostok',
'2021-06-20T00:00:00.000000+10:00', '2021-06-21T00:00:00.000000+10:00'
),
(
'1', 'picking_duration_per_item', 'day', 13.1, 13, '2021-06-21T00:00:00.000000+10:00',
'Asia/Vladivostok',
'2021-06-20T00:00:00.000000+10:00', '2021-06-21T00:00:00.000000+10:00'
),
(
'1', 'delivery_rate', 'day', 14.1, 14, '2021-06-22T09:00:00.000000+10:00',
'Asia/Vladivostok',
'2021-06-21T00:00:00.000000+10:00', '2021-06-22T00:00:00.000000+10:00'
),
(
'1', 'delivery_rate', 'day', 15.1, 15, '2021-06-22T18:00:00.000000+10:00',
'Asia/Vladivostok',
'2021-06-21T00:00:00.000000+10:00', '2021-06-22T00:00:00.000000+10:00'
),
(
'1', 'delivery_rate', 'day', 16.1, 16, '2021-06-23T00:00:00.000000+10:00',
'Asia/Vladivostok',
'2021-06-22T00:00:00.000000+10:00', '2021-06-23T00:00:00.000000+10:00'
),
(
'1', 'delivery_rate', 'day', 17.1, 17, '2021-06-24T23:59:59.999999+10:00',
'Asia/Vladivostok',
'2021-06-23T00:00:00.000000+10:00', '2021-06-24T00:00:00.000000+10:00'
),
('2', 'delivery_rate', 'day', 21.1, 21, '2021-06-21T00:00:00.000000+03:00',
'Europe/Moscow',
'2021-06-20T00:00:00.000000+03:00', '2021-06-21T00:00:00.000000+03:00'
),
(
'2', 'delivery_rate', 'day', 22.1, 22, '2021-06-21T23:59:59.999999+03:00',
'Europe/Moscow',
'2021-06-20T00:00:00.000000+03:00', '2021-06-21T00:00:00.000000+03:00'
),
(
'2', 'picking_duration_per_item', 'day', 23.1, 23, '2021-06-21T00:00:00.000000+03:00',
'Europe/Moscow',
'2021-06-20T00:00:00.000000+03:00', '2021-06-21T00:00:00.000000+03:00'
),
(
'2', 'delivery_rate', 'day', 24.1, 24, '2021-06-22T09:00:00.000000+03:00',
'Europe/Moscow',
'2021-06-21T00:00:00.000000+03:00', '2021-06-22T00:00:00.000000+03:00'
),
(
'2', 'delivery_rate', 'day', 25.1, 25, '2021-06-22T18:00:00.000000+03:00',
'Europe/Moscow',
'2021-06-21T00:00:00.000000+03:00', '2021-06-22T00:00:00.000000+03:00'
),
(
'2', 'delivery_rate', 'day', 26.1, 26, '2021-06-23T00:00:00.000000+03:00',
'Europe/Moscow',
'2021-06-22T00:00:00.000000+03:00', '2021-06-23T00:00:00.000000+03:00'
),
(
'2', 'delivery_rate', 'day', 27.1, 27, '2021-06-24T23:59:59.999999+03:00',
'Europe/Moscow',
'2021-06-23T00:00:00.000000+03:00', '2021-06-24T00:00:00.000000+03:00'
),
(
'3', 'complete_orders_count', 'day', 30, 30, '2021-06-21T00:00:00.000000+05:00',
'Asia/Yekaterinburg',
'2021-06-20T00:00:00.000000+05:00', '2021-06-21T00:00:00.000000+05:00'
);
