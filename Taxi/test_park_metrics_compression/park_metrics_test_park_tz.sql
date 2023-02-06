INSERT INTO metrics.park_hourly_metrics(
    park_id,
    date_at,
    metrics
)
VALUES
(
    'park3',
    '2019-12-25T12:00:00+00',
    '{"successful": 26}'::jsonb
);

INSERT INTO metrics.park_daily_metrics (
    park_id,
    date_at,
    metrics
)
VALUES
(
    'park3',
    '2019-12-25T00:00:00+00',
    '{"successful": 25}'::jsonb
);
