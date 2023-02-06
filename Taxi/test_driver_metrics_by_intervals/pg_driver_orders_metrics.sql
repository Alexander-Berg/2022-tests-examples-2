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
  '2020-03-17 05:00:00+03',
  '{"successful": 5, "successful_cash": 4, "driver_cancelled": 3, "successful_econom": 2, "successful_cashless": 1}'
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
  'driver_id_1',
  '2020-03-20 03:00:00+03',
  '{"successful": 5, "successful_cash": 4, "driver_cancelled": 3, "successful_econom": 2, "successful_cashless": 1}'
);

