INSERT INTO metrics.park_hourly_metrics(
  park_id,
  date_at,
  metrics)
VALUES (
  'park_id_1',
  '2020-03-17 03:00:00+03',
  '{"successful": 1, "successful_cash": 2, "driver_cancelled": 3, '
  '"successful_econom": 4, "successful_cashless": 5, "successful_active_drivers": 111}'
),
(
  'park_id_1',
  '2020-03-17 05:00:00+03',
  '{"successful": 5, "successful_cash": 4, "driver_cancelled": 3, '
  '"successful_econom": 2, "successful_cashless": 1, "successful_active_drivers": 222}'
),
(
  'park_id_1',
  '2020-03-18 17:00:00+03',
  '{"successful_active_drivers": 888, "successful": 9}'
);

INSERT INTO metrics.park_daily_metrics(
  park_id,
  date_at,
  metrics)
VALUES (
  'park_id_1',
  '2020-03-18 00:00:00+00',
  '{"successful": 1, "successful_cash": 2, "driver_cancelled": 3, '
  '"successful_econom": 4, "successful_cashless": 5, "successful_active_drivers": 333}'
),
(
  'park_id_1',
  '2020-03-20 03:00:00+03',
  '{"successful": 5, "successful_cash": 4, "driver_cancelled": 3, '
  '"successful_econom": 2, "successful_cashless": 1, "successful_active_drivers": 444}'
);

