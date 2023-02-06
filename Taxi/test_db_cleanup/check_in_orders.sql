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
  NOW(),
  NOW(),
  NULL,
  'terminal_id1',
  NULL,
  'some_tariff_zone',
  'some_user',
  'some_phone_id',
  'some_locale',
  '{econom, comfortplus}'
),
(
  'order_id2',
  NOW(),
  NOW() - INTERVAL '121 minutes',
  NOW(),
  'terminal_id2',
  'pickup_line1',
  'some_tariff_zone',
  'some_user',
  'some_phone_id',
  'some_locale',
  '{business}'
);
