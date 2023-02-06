INSERT INTO metrics.park_daily_metrics (
    park_id,
    date_at,
    metrics
)
VALUES
(
    'park1',
    '2019-12-27T00:00:00+00',
    '{"successful": 4, "metric1": 228}'::jsonb
);
