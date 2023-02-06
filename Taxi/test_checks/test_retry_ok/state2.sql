INSERT INTO fleet_drivers_scoring.check_parts
(
    id,
    unique_driver_id,
    part_type,
    internal_revision,
    created_at,
    data
)
VALUES
(
    'id1',
    'udid1',
    'ratings_history',
    '2020-05-04T00:00:00',
    '2020-04-20T00:00:00+00:00',
    '{
       "response": {
         "version": "1",
         "data": {
           "ratings_history": [
             {
               "begin_at": "2020-04-20T00:00:00.0Z",
               "end_at": "2020-04-27T00:00:00.0Z",
               "rating": 5.0
             }
           ]
         }
       }
    }'::jsonb
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
    is_orders_statistics_calculated,
    quality_metrics_id,
    is_quality_metrics_calculated
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
    FALSE,
    NULL,
    FALSE,
    NULL,
    FALSE
);
