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
),
(
    'id3',
    'udid1',
    'quality_metrics',
    '2020-05-06T00:00:00',
    '2020-04-20T00:00:00+00:00',
    '{
        "response": {
          "data": {
            "road_accidents": {
              "insured_events": {
                "begin_at": "2019-01-01T03:00:00+03:00",
                "events_number": 0
              }
            },
            "passenger_feedback_statistics": {
              "begin_at": "2019-01-01T03:00:00+03:00",
              "negative_tag_amounts": {
                "no_trip": 17,
                "no_change": 2,
                "driver_late": 0,
                "rude_driver": 6,
                "circle_driving": 0,
                "smelly_vehicle": 7,
                "unsafe_driving": 5,
                "driver_impolite": 2,
                "vehicle_condition": 4
              },
              "positive_tag_amounts": {
                "clean": 108,
                "music": 71,
                "polite": 91,
                "good_mood": 60,
                "comfort_ride": 139,
                "pleasant_conversation": 52
              },
              "feedbacks_number": 903
            }
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
    'id3',
    TRUE
);
