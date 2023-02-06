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
    'orders_statistics',
    '2020-04-30',
    CURRENT_TIMESTAMP,
    '{
       "response": {
         "data": {
           "total_statistics": {
             "begin_at": "2019-01-01T03:00:00+03:00",
             "successful_orders_count": 10,
             "driver_rejected_orders_count": 5
           },
           "first_and_last_order": {
             "first_order_at": "2014-06-30 14:47:47.052+00:00",
             "last_order_at": "2019-06-30 14:47:47.052+00:00"
           },
           "statistics_by_interval": [
             {
               "begin_at": "2020-02-01T03:00:00+03:00",
               "end_at": "2020-03-01T03:00:00+03:00",
               "tariffs_statistics": [
                 {
                   "tariff": "econom",
                   "successful_orders_count": 83,
                   "driver_rejected_orders_count": 1
                 },
                 {
                   "tariff": "comfort",
                   "successful_orders_count": 1,
                   "driver_rejected_orders_count": 1
                 }
               ]
             }
           ]
         },
         "version": "1"
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
    orders_statistics_id,
    is_orders_statistics_calculated
)
VALUES
(
    'park1',
    'req_done',
    '1',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP,
    'license_pd_id',
    'done',
    'id1',
    TRUE
),
(
    'park1',
    'req_no_orders_statistics',
    '2',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP,
    'license_pd_id2',
    'done',
    NULL,
    TRUE
)
;
