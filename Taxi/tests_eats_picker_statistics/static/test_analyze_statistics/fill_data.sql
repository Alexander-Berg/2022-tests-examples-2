insert into eats_picker_statistics.statistics (
    picker_id,
    metric_name,
    metric_interval,
    value,
    final_items_count,
    created_at,
    picker_timezone,
    utc_from,
    utc_to
)
values (
'1', 'picking_duration_per_item', 'day', 115.1, 21, '2021-04-21T21:00:00.000000+00:00',
'Europe/Moscow',
'2021-04-21T00:00:00.000000+03:00', '2021-04-22T00:00:00.000000+03:00'
),
(
'1', 'delivery_rate', 'day', 1.5, 21, '2021-04-21T00:00:00.000000+00:00',
'Europe/Moscow',
'2021-04-21T00:00:00.000000+03:00', '2021-04-22T00:00:00.000000+03:00'
),
(
'1', 'picking_duration_per_item', 'day', 110.129, 21, '2021-04-23T00:00:00.000000+00:00',
'Europe/Moscow',
'2021-04-22T00:00:00.000000+03:00', '2021-04-23T00:00:00.000000+03:00'
),
(
'1', 'delivery_rate', 'day', 1.1111, 21, '2021-04-23T00:00:00.000000+00:00',
'Europe/Moscow',
'2021-04-22T00:00:00.000000+03:00', '2021-04-23T00:00:00.000000+03:00'
),
(
'1', 'delivery_rate', 'day', 1.2, 21, '2021-04-25T00:00:00.000000+00:00',
'Europe/Moscow',
'2021-04-24T00:00:00.000000+03:00', '2021-04-25T00:00:00.000000+03:00'
),
(
'1', 'delivery_rate', 'day', 1.7, 28, '2021-04-25T00:00:01.000000+00:00',
'Europe/Moscow',
'2021-04-24T00:00:00.000000+03:00', '2021-04-25T00:00:00.000000+03:00'
),
(
'1', 'picking_duration_per_item', 'day', 122.83, 21, '2021-04-25T00:00:01.000000+00:00',
'Europe/Moscow',
'2021-04-24T00:00:00.000000+03:00', '2021-04-25T00:00:00.000000+03:00'
),
(
'2', 'picking_duration_per_item', 'day', 130.2, 22, '2021-04-23T00:00:00.000000+00:00',
'Europe/Moscow',
'2021-04-22T00:00:00.000000+03:00', '2021-04-23T00:00:00.000000+03:00'
),
(
'2', 'delivery_rate', 'day', 1.2, 22, '2021-04-23T00:00:00.000000+00:00',
'Europe/Moscow',
'2021-04-22T00:00:00.000000+03:00', '2021-04-23T00:00:00.000000+03:00'
),
(
'3', 'picking_duration_per_item', 'day', 110.3, 23, '2021-04-23T00:00:00.000000+00:00',
'Europe/Moscow',
'2021-04-22T00:00:00.000000+03:00', '2021-04-23T00:00:00.000000+03:00'
),
(
'3', 'delivery_rate', 'day', 0.93, 23, '2021-04-23T00:00:00.000000+00:00',
'Europe/Moscow',
'2021-04-22T00:00:00.000000+03:00', '2021-04-23T00:00:00.000000+03:00'
),
(
'4', 'picking_duration_per_item', 'day', 130.4, 24, '2021-04-23T00:00:00.000000+00:00',
'Europe/Moscow',
'2021-04-22T00:00:00.000000+03:00', '2021-04-23T00:00:00.000000+03:00'
),
(
'4', 'delivery_rate', 'day', 0.94, 24, '2021-04-23T00:00:00.000000+00:00',
'Europe/Moscow',
'2021-04-22T00:00:00.000000+03:00', '2021-04-23T00:00:00.000000+03:00'
),
(
'5', 'picking_duration_per_item', 'week', 115.5, 25, '2021-04-21T00:00:00.000000+00:00',
'Europe/Moscow',
'2021-04-14T00:00:00.000000+03:00', '2021-04-21T00:00:00.000000+03:00'
),
(
'5', 'delivery_rate', 'week', 1.6, 25, '2021-04-21T00:00:00.000000+00:00',
'Europe/Moscow',
'2021-04-14T00:00:00.000000+03:00', '2021-04-21T00:00:00.000000+03:00'
),
(
'5', 'picking_duration_per_item', 'week', 110.5, 25, '2021-04-23T00:00:00.000000+00:00',
'Europe/Moscow',
'2021-04-16T00:00:00.000000+03:00', '2021-04-23T00:00:00.000000+03:00'
),
(
'5', 'delivery_rate', 'week', 1.5, 25, '2021-04-23T00:00:00.000000+00:00',
'Europe/Moscow',
'2021-04-16T00:00:00.000000+03:00', '2021-04-23T00:00:00.000000+03:00'
),
(
'6', 'picking_duration_per_item', 'week', 130.6, 26, '2021-04-23T00:00:00.000000+00:00',
'Europe/Moscow',
'2021-04-16T00:00:00.000000+03:00', '2021-04-23T00:00:00.000000+03:00'
),
(
'6', 'delivery_rate', 'week', 1.6, 26, '2021-04-23T00:00:00.000000+00:00',
'Europe/Moscow',
'2021-04-16T00:00:00.000000+03:00', '2021-04-23T00:00:00.000000+03:00'
),
(
'7', 'picking_duration_per_item', 'week', 110.7, 27, '2021-04-23T00:00:00.000000+00:00',
'Europe/Moscow',
'2021-04-16T00:00:00.000000+03:00', '2021-04-23T00:00:00.000000+03:00'
),
('7', 'delivery_rate', 'week', 0.97, 27, '2021-04-23T00:00:00.000000+00:00',
'Europe/Moscow',
'2021-04-16T00:00:00.000000+03:00', '2021-04-23T00:00:00.000000+03:00'
),
(
'8', 'picking_duration_per_item', 'week', 130.8, 28, '2021-04-23T00:00:00.000000+00:00',
'Europe/Moscow',
'2021-04-16T00:00:00.000000+03:00', '2021-04-23T00:00:00.000000+03:00'
),
(
'8', 'delivery_rate', 'week', 0.98, 28, '2021-04-23T00:00:00.000000+00:00',
'Europe/Moscow',
'2021-04-16T00:00:00.000000+03:00', '2021-04-23T00:00:00.000000+03:00'
),
(
'9', 'picking_duration_per_item', 'day', 120.9, 9, '2021-04-23T00:00:00.000000+00:00',
'Europe/Moscow',
'2021-04-22T00:00:00.000000+03:00', '2021-04-23T00:00:00.000000+03:00'
),
(
'9', 'delivery_rate', 'day', 1.9, 9, '2021-04-23T00:00:00.000000+00:00',
'Europe/Moscow',
'2021-04-22T00:00:00.000000+03:00', '2021-04-23T00:00:00.000000+03:00'
),
(
'9', 'picking_duration_per_item', 'week', 120.9, 29, '2021-04-23T00:00:00.000000+00:00',
'Europe/Moscow',
'2021-04-16T00:00:00.000000+03:00', '2021-04-23T00:00:00.000000+03:00'
),
(
'9', 'delivery_rate', 'week', 1.9, 29, '2021-04-23T00:00:00.000000+00:00',
'Europe/Moscow',
'2021-04-16T00:00:00.000000+03:00', '2021-04-23T00:00:00.000000+03:00'
),
(
'10', 'picking_duration_per_item', 'day', 120.0, 5, '2021-04-24T00:00:00.000000+00:00',
'Europe/Moscow',
'2021-04-23T00:00:00.000000+03:00', '2021-04-24T00:00:00.000000+03:00'
),
(
'10', 'delivery_rate', 'day', 1.0, 5, '2021-04-24T00:00:00.000000+00:00',
'Europe/Moscow',
'2021-04-23T00:00:00.000000+03:00', '2021-04-24T00:00:00.000000+03:00'
),
(
'10', 'picking_duration_per_item', 'week', 120.0, 5, '2021-04-24T00:00:00.000000+00:00',
'Europe/Moscow',
'2021-04-17T00:00:00.000000+03:00', '2021-04-24T00:00:00.000000+03:00'
),
(
'10', 'delivery_rate', 'week', 1.0, 5, '2021-04-24T00:00:00.000000+00:00',
'Europe/Moscow',
'2021-04-17T00:00:00.000000+03:00', '2021-04-24T00:00:00.000000+03:00'
),
(
'11', 'picking_duration_per_item', 'month', 111.1, 21, '2021-04-21T00:00:00.000000+00:00',
'Europe/Moscow',
'2021-03-21T00:00:00.000000+03:00', '2021-04-21T00:00:00.000000+03:00'
),
(
'11', 'delivery_rate', 'month', 11.1, 21, '2021-04-21T00:00:00.000000+00:00',
'Europe/Moscow',
'2021-03-21T00:00:00.000000+03:00', '2021-04-21T00:00:00.000000+03:00'
),
(
'11', 'picking_duration_per_item', 'month', 111.111, 21, '2021-04-23T00:00:00.000000+00:00',
'Europe/Moscow',
'2021-03-23T00:00:00.000000+03:00', '2021-04-23T00:00:00.000000+03:00'
),
(
'11', 'delivery_rate', 'month', 123.45, 21, '2021-04-23T00:00:00.000000+00:00',
'Europe/Moscow',
'2021-03-23T00:00:00.000000+03:00', '2021-04-23T00:00:00.000000+03:00'
),
(
'11', 'delivery_rate', 'month', 666, 21, '2021-04-25T00:00:00.000000+00:00',
'Europe/Moscow',
'2021-03-25T00:00:00.000000+03:00', '2021-04-25T00:00:00.000000+03:00'
),
(
'12', 'picking_duration_per_item', 'month', 222.1, 22, '2021-04-02T00:00:00.000000+00:00',
'Asia/Yekaterinburg',
'2021-03-02T00:00:00.000000+05:00', '2021-04-02T00:00:00.000000+05:00'
),
(
'12', 'delivery_rate', 'month', 22.1, 22, '2021-04-02T00:00:00.000000+00:00',
'Asia/Yekaterinburg',
'2021-03-02T00:00:00.000000+05:00', '2021-04-02T00:00:00.000000+05:00'
),
(
'12', 'picking_duration_per_item', 'month', 222.2, 22, '2021-04-02T00:00:01.000000+00:00',
'Asia/Yekaterinburg',
'2021-03-02T00:00:00.000000+05:00', '2021-04-02T00:00:00.000000+05:00'
),
(
'12', 'delivery_rate', 'month', 22.2, 22, '2021-04-02T00:00:01.000000+00:00',
'Asia/Yekaterinburg',
'2021-03-02T00:00:00+05:00', '2021-04-02T00:00:00+05:00'
),
(
'13', 'picking_duration_per_item', 'day', 13.13, 13, '2021-05-31T23:00:00.000000+05:00',
'Europe/Moscow',
'2021-05-30T00:00:00.000000+05:00', '2021-05-31T00:00:00.000000+05:00'
),
(
'13', 'delivery_rate', 'day', 13.13, 13, '2021-05-31T23:00:00.000000+05:00',
'Europe/Moscow',
'2021-05-30T00:00:00.000000+05:00', '2021-05-31T00:00:00.000000+05:00'
);