INSERT INTO metrics.driver_hourly_metrics(
  park_id,
  driver_id,
  date_at,
  metrics)
VALUES (
  'park_id_1',
  'driver_id_1',
  '2020-03-17 03:00:00+03',
  '{"successful": 1, "successful_cash": 2, "driver_cancelled": 3, "successful_econom": 4, "successful_cashless": 5}'
),
(
  'park_id_1',
  'driver_id_1',
  '2020-03-17 04:00:00+03',
  '{"successful": 1, "successful_cash": 2, "driver_cancelled": 3, "successful_econom": 4, "successful_cashless": 5}'
),
(
  'park_id_1',
  'driver_id_2',
  '2020-03-17 03:00:00+03',
  '{"successful": 2, "successful_cash": 1, "successful_econom": 4, "successful_cashless": 5}'
);

INSERT INTO metrics.driver_daily_metrics(
  park_id,
  driver_id,
  date_at,
  metrics)
VALUES (
  'park_id_1',
  'driver_id_1',
  '2020-03-18 00:00:00+00',
  '{"successful": 1, "successful_cash": 2, "driver_cancelled": 3, "successful_econom": 4, "successful_cashless": 5}'
),
(
  'park_id_1',
  'driver_id_2',
  '2020-03-19 00:00:00+00',
  '{"successful": 1, "successful_cash": 2, "driver_cancelled": 3, "successful_econom": 4, "successful_cashless": 5}'
),
(
  'park_id_1',
  'driver_id_2',
  '2020-03-20 00:00:00+00',
  '{"successful": 5}'
);
