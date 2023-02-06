INSERT INTO metrics.park_hourly_metrics(
    park_id,
    date_at,
    metrics
)
VALUES
(
    'park1',
    '2019-12-27T10:00:00+00',
    '{"driver_cancelled": 1, "successful": 1}'::jsonb
),
(
    'park1',
    '2019-12-27T11:00:00+00',
    '{"driver_cancelled": 1, "successful": 1, "successful_econom": 3}'::jsonb
),
(
    'park1',
    '2019-12-27T23:00:00+00',
    '{"driver_cancelled": 1, "successful": 1, "client_cancelled": 3}'::jsonb
),
(
    'unknown_park',
    '2018-03-28T13:00:00+00',
    '{"successful": 123}'::jsonb
);


INSERT INTO metrics.park_daily_metrics(
    park_id,
    date_at,
    metrics
)
VALUES
(
    'park1',
    '2019-12-26T00:00:00+00',
    '{"driver_cancelled": 26}'::jsonb
);
