INSERT INTO metrics.park_daily_metrics(
  park_id,
  date_at,
  metrics)
VALUES (
  'park_id_1',
  '2019-03-17 00:00:00+03:00',
  '{"successful": 1, "successful_cash": 2, "driver_cancelled": 3, "successful_econom": 4, "successful_cashless": 5}'
),
(
  'park_id_1',
  '2019-03-18 00:00:00+03:00',
  '{"successful": 1, "successful_cash": 2, "driver_cancelled": 3, "successful_econom": 4, "successful_cashless": 5}'
);

INSERT INTO metrics.driver_daily_metrics(
  park_id,
  driver_id,
  date_at,
  metrics)
VALUES (
  'park_id_1',
  'driver_id_1',
  '2019-03-15 00:00:00+03:00',
  '{"successful": 1, "successful_cash": 2, "driver_cancelled": 3, "successful_econom": 4, "successful_cashless": 5}'
),
(
  'park_id_1',
  'driver_id_1',
  '2019-03-16 00:00:00+03:00',
  '{"successful": 1, "successful_cash": 2, "driver_cancelled": 3, "successful_econom": 4, "successful_cashless": 5}'
),
(
  'park_id_1',
  'driver_id_1',
  '2019-03-17 00:00:00+03:00',
  '{"successful": 1, "successful_cash": 2, "driver_cancelled": 3, "successful_econom": 4, "successful_cashless": 5}'
),
(
  'park_id_1',
  'driver_id_1',
  '2019-03-18 00:00:00+03:00',
  '{"successful": 1, "successful_cash": 2, "driver_cancelled": 3, "successful_econom": 4, "successful_cashless": 5}'
);
