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
),
(
    'id2',
    'udid1',
    'orders_statistics',
    '2020-05-05T00:00:00',
    '2020-04-20T00:00:00+00:00',
    '{
       "response": {
         "version": "1",
         "data": {
           "statistics_by_interval": [],
           "total_statistics": {
             "begin_at": "2019-11-07T00:00:00+00:00",
             "driver_rejected_orders_count": 5,
             "successful_orders_count": 10
           },
           "first_and_last_order": {
             "first_order_at": "2014-06-30 14:47:47.052+00:00",
             "last_order_at": "2019-06-30 14:47:47.052+00:00"
           }
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
    'id1',
    TRUE,
    'id2',
    TRUE,
    NULL,
    FALSE
);
