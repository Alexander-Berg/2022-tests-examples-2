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
    'quality_metrics',
    '2020-06-05',
    CURRENT_TIMESTAMP,
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
    quality_metrics_id,
    is_quality_metrics_calculated
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
    'req_no_quality_metrics',
    '2',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP,
    'license_pd_id2',
    'done',
    NULL,
    TRUE
)
;
