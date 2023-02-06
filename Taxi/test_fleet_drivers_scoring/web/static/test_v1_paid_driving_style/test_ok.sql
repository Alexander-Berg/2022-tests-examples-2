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
    'driving_style',
    '2020-04-30',
    CURRENT_TIMESTAMP,
    '{
       "response": {
         "data": {
           "aggressive_driving_orders_percentage": 22,
           "worse_than_drivers_percent": 80,
           "aggressive_driving_frequency": "medium"
         },
         "version": "1"
       }
    }'::jsonb
),
(
    'id3',
    'udid1',
    'driving_style',
    '2020-04-29',
    CURRENT_TIMESTAMP,
    '{}'::jsonb
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
    driving_style_id,
    is_driving_style_calculated
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
),
(
    'park1',
    'req_not_enough_data',
    '3',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP,
    'license_pd_id2',
    'done',
    'id3',
    TRUE
)
;
