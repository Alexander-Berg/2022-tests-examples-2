INSERT INTO metrics.driver_hourly_metrics(
    park_id,
    driver_id,
    date_at,
    metrics
)
VALUES
(
    'park1',
    'driver1',
    '2019-12-27T13:00:00+03',
    '{"driver_cancelled": 2, "successful": 3, "successful_active_drivers": 5}'::jsonb
),
(
    'park1',
    'driver1',
    '2019-12-27T11:00:00+00',
    '{"driver_cancelled": 3, "successful": 3, "successful_econom": 1, "successful_active_drivers": 7}'::jsonb
),
(
    'park1',
    'driver1',
    '2019-12-27T23:00:00+00',
    '{"driver_cancelled": 4, "successful": 3, "client_cancelled": 1}'::jsonb
),
(
    'park1',
    'driver2',
    '2025-03-28T13:00:00+00',
    '{"successful": 322}'::jsonb
),
(
    'park2',
    'driver1',
    '2019-12-12T13:00:00+00',
    '{"successful": 555}'::jsonb
);

INSERT INTO metrics.driver_daily_metrics (
    park_id,
    driver_id,
    date_at,
    metrics
)
VALUES
(
    'park1',
    'driver1',
    '2019-12-27T00:00:00+00',
    '{"driver_cancelled": 3, "successful": 4}'::jsonb
),
(
    'park1',
    'driver2',
    '2019-12-28T00:00:00+00',
    '{"successful": 322}'::jsonb
),
(
    'park2',
    'driver1',
    '2019-12-31T00:00:00+00',
    '{"successful": 223}'::jsonb
);
