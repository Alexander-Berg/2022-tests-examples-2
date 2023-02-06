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
    car_orders_history_id,
    is_car_orders_history_calculated
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

