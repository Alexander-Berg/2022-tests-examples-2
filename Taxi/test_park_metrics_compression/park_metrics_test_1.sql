INSERT INTO metrics.park_hourly_metrics(
    park_id,
    date_at,
    metrics
)
VALUES
(
    'park1',
    '2019-12-27T13:00:00+03',
    '{"driver_cancelled": 2, "successful": 3}'::jsonb
),
(
    'park1',
    '2019-12-27T11:00:00+00',
    '{"driver_cancelled": 3, "successful": 3, "successful_econom": 1}'::jsonb
),
(
    'park1',
    '2019-12-27T23:00:00+00',
    '{"driver_cancelled": 4, "successful": 3, "client_cancelled": 1}'::jsonb
),
(
    'park1',
    '2025-03-28T13:00:00+00',
    '{"successful": 322}'::jsonb
);

INSERT INTO metrics.park_daily_metrics (
    park_id,
    date_at,
    metrics
)
VALUES
(
    'park1',
    '2019-12-27T00:00:00+00',
    '{"driver_cancelled": 3, "successful": 4}'::jsonb
),
(
    'park1',
    '2019-12-28T00:00:00+00',
    '{"successful": 322}'::jsonb
);
