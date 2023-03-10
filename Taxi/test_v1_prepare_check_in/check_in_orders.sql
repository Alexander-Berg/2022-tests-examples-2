INSERT INTO dispatch_check_in.check_in_orders (
  order_id,
  updated_ts,
  created_ts,
  check_in_ts,
  terminal_id,
  pickup_line,
  tariff_zone,
  user_id,
  user_phone_id,
  user_locale,
  classes
) VALUES
-- 4 orders with check in time and 
-- 5 orders without check in time
(
  'order_id1',
  '2021-06-04T13:37:02.08513+00:00',
  '2021-06-04T13:37:02.08513+00:00',
  '2021-06-04T13:37:02.08513+00:00',
  'svo_test_order_queue_overflow',
  'svo_line_1',
  'some_tariff_zone',
  'some_user',
  'some_phone_id',
  'some_locale',
  '{econom}'
),
(
  'order_id2',
  '2021-06-04T13:37:02.08513+00:00',
  '2021-06-04T13:37:02.08513+00:00',
  '2021-06-04T13:37:02.08513+00:00',
  'svo_test_order_queue_overflow',
  'svo_line_1',
  'some_tariff_zone',
  'some_user',
  'some_phone_id',
  'some_locale',
  '{econom}'
),
(
  'order_id3',
  '2021-06-04T13:37:02.08513+00:00',
  '2021-06-04T13:37:02.08513+00:00',
  '2021-06-04T13:37:02.08513+00:00',
  'svo_test_order_queue_overflow',
  'svo_line_1',
  'some_tariff_zone',
  'some_user',
  'some_phone_id',
  'some_locale',
  '{econom}'
),
(
  'order_id4',
  '2021-06-04T13:37:02.08513+00:00',
  '2021-06-04T13:37:02.08513+00:00',
  '2021-06-04T13:37:02.08513+00:00',
  'svo_test_order_queue_overflow',
  'svo_line_1',
  'some_tariff_zone',
  'some_user',
  'some_phone_id',
  'some_locale',
  '{econom}'
),
(
  'order_id5',
  '2021-06-04T13:37:02.08513+00:00',
  '2021-06-04T13:37:02.08513+00:00',
  NULL,
  'svo_test_order_queue_overflow',
  NULL,
  'some_tariff_zone',
  'some_user',
  'some_phone_id',
  'some_locale',
  '{econom}'
),
(
  'order_id6',
  '2021-06-04T13:37:02.08513+00:00',
  '2021-06-04T13:37:02.08513+00:00',
  NULL,
  'svo_test_order_queue_overflow',
  NULL,
  'some_tariff_zone',
  'some_user',
  'some_phone_id',
  'some_locale',
  '{econom}'
),
(
  'order_id7',
  '2021-06-04T13:37:02.08513+00:00',
  '2021-06-04T13:37:02.08513+00:00',
  NULL,
  'svo_test_order_queue_overflow',
  NULL,
  'some_tariff_zone',
  'some_user',
  'some_phone_id',
  'some_locale',
  '{econom}'
),
(
  'order_id8',
  '2021-06-04T13:37:02.08513+00:00',
  '2021-06-04T13:37:02.08513+00:00',
  NULL,
  'svo_test_order_queue_overflow',
  NULL,
  'some_tariff_zone',
  'some_user',
  'some_phone_id',
  'some_locale',
  '{econom}'
),
(
  'order_id9',
  '2021-06-04T13:37:02.08513+00:00',
  '2021-06-04T13:37:02.08513+00:00',
  NULL,
  'svo_test_order_queue_overflow',
  NULL,
  'some_tariff_zone',
  'some_user',
  'some_phone_id',
  'some_locale',
  '{econom}'
);
