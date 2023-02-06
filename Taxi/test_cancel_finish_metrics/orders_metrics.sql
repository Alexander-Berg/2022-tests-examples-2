INSERT INTO eats_order_stats_v2.orders_metrics_data
(
    sensor, brand_name, order_type, shipping_type, cancellation_reason, last_order_at, counter_value
)
VALUES
('order_cancelled', 'BRAND_NAME1', 'native',   'pickup', 'some_reason', '2021-05-27 18:32:00+03', 2),
('order_cancelled', 'BRAND_NAME2', 'native',   'pickup', 'some_reason', '2021-05-27 18:32:00+03', 4),
('order_cancelled',       'other', 'native',   'pickup', 'some_reason', '2021-05-27 18:32:00+03', 6),
('order_cancelled', 'BRAND_NAME1', 'native', 'delivery', 'some_reason', '2021-05-27 18:32:00+03', 2),
('order_cancelled', 'BRAND_NAME2', 'native', 'delivery', 'some_reason', '2021-05-27 18:32:00+03', 4),
('order_cancelled',       'other', 'native', 'delivery', 'some_reason', '2021-05-27 18:32:00+03', 6),
( 'order_finished', 'BRAND_NAME1', 'native',   'pickup',          NULL, '2021-05-27 18:32:00+03', 2),
( 'order_finished', 'BRAND_NAME2', 'native',   'pickup',          NULL, '2021-05-27 18:32:00+03', 4),
( 'order_finished',       'other', 'native',   'pickup',          NULL, '2021-05-27 18:32:00+03', 6),
( 'order_finished', 'BRAND_NAME1', 'native', 'delivery',          NULL, '2021-05-27 18:32:00+03', 2),
( 'order_finished', 'BRAND_NAME2', 'native', 'delivery',          NULL, '2021-05-27 18:32:00+03', 4),
( 'order_finished',       'other', 'native', 'delivery',          NULL, '2021-05-27 18:32:00+03', 6);
