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
    'passenger_tags',
    '2020-04-30',
    CURRENT_TIMESTAMP,
    '{
        "response": {
          "data": {
            "top_negative_tags": [
              {
                "frequency_commpared_with_average_percent": 20,
                "name": "driver_impolite"
              },
              {
                "frequency_commpared_with_average_percent": 12.5,
                "name": "smelly_vehicle"
              }
            ],
            "top_positive_tags": [
              {
                "frequency_commpared_with_average_percent": -10,
                "name": "tag_mood"
              }
            ]
          },
          "version": "1"
        }
    }
    '::jsonb
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
    passenger_tags_id,
    is_passenger_tags_calculated
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
    'req_no_data',
    '2',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP,
    'license_pd_id2',
    'done',
    NULL,
    TRUE
)
;
