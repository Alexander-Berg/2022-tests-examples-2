INSERT INTO fleet_drivers_scoring.yt_updates
(
    id,
    name,
    path,
    revision,
    created_at
)
VALUES
(
    1,
    'orders',
    '//home/opteum/fm/testing/features/scoring/orders_statistics/2020-05-06',
    '2020-05-04',
    CURRENT_TIMESTAMP
);

INSERT INTO fleet_drivers_scoring.checks
(
    park_id,
    check_id,
    idempotency_token,
    created_at,
    updated_at,
    license_pd_id,
    status,
    ratings_history_id,
    is_ratings_history_calculated,
    orders_statistics_id,
    is_orders_statistics_calculated
    -- all other parts ids have default values NULL, TRUE
)
VALUES
(
    'park1',
    'req_1',
    'req_1',
    '2020-04-20T00:00:00+00:00',
    '2020-04-20T00:00:00+00:00',
    'license_pd_id',
    'pending',
    NULL,
    TRUE,
    NULL,
    FALSE
);

