INSERT INTO fleet_drivers_scoring.checks
(
    park_id,
    check_id,
    idempotency_token,
    created_at,
    updated_at,
    license_pd_id,
    status,
    is_ratings_history_calculated,
    is_orders_statistics_calculated,
    is_quality_metrics_calculated,
    is_high_speed_driving_calculated,
    is_passenger_tags_calculated,
    is_driving_style_calculated
)
VALUES
(
    'park1',
    'req_done',
    '1',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP,
    'license_pd_id1',
    'done',
    FALSE,
    FALSE,
    FALSE,
    FALSE,
    FALSE,
    FALSE
),
(
    'park1',
    'req_pending',
    '2',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP,
    'license_pd_id2',
    'pending',
    FALSE,
    FALSE,
    FALSE,
    FALSE,
    FALSE,
    FALSE
)
;

INSERT INTO fleet_drivers_scoring.rates
(
    clid,
    day,
    period,
    type,
    amount,
    rate_limit,
    created_at,
    updated_at
)
VALUES
(
    'clid1',
    '2020-02-02',
    'day',
    'free',
    1,
    10,
    '2019-02-02 01:00:00.0+00',
    '2019-02-02 01:21:00.0+00'
),
(
    'clid1',
    '2020-01-27',
    'week',
    'free',
    2,
    10,
    '2019-02-02 01:00:00.0+00',
    '2019-02-02 01:21:00.0+00'
)
;

