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
(
  'order_id1',
  '2021-06-04T13:37:02.08513+00:00',
  '2021-06-04T13:37:02.08513+00:00',
  '2021-06-04T13:37:02.08513+00:00',
  'svo',
  'svo_d_line_1',
  'some_tarifff_zone',
  'some_user',
  'some_phone_id',
  'some_locale',
  '{econom}'
);
