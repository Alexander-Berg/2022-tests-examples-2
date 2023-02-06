INSERT INTO eats_tips_payments.orders (
  order_id,
  yandex_user_id,
  amount,
  cashback_status,
  plus_amount,
  created_at
)
VALUES
(1, 'failed-10min-ago', 100, 'failed', 10, NOW() AT TIME ZONE 'utc' - INTERVAL '10 MINUTES'),
(2, 'failed-15min-ago', 100, 'failed', 10, NOW() AT TIME ZONE 'utc' - INTERVAL '15 MINUTES'),
(3, 'in-progress-1min', 100, 'in-progress', 10, NOW() AT TIME ZONE 'utc' - INTERVAL '1 MINUTES'),
(4, 'in-progress-5min', 100, 'in-progress', 10, NOW() AT TIME ZONE 'utc' - INTERVAL '5 MINUTES'),
(5, 'in-progress-10min', 100, 'in-progress', 10, NOW() AT TIME ZONE 'utc' - INTERVAL '10 MINUTES'),
(6, 'success-5min', 100, 'success', 10, NOW() AT TIME ZONE 'utc' - INTERVAL '5 MINUTES'),
(7, 'success-10min', 100, 'success', 10, NOW() AT TIME ZONE 'utc' - INTERVAL '10 MINUTES'),
(8, 'null', 100, NULL, 10, NOW() AT TIME ZONE 'utc' - INTERVAL '2 MINUTES');
