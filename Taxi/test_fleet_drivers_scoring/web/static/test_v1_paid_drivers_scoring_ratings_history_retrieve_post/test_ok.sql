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
    '2020-04-30',
    CURRENT_TIMESTAMP,
    '{
        "response": {
            "version": "1",
            "data": {
                "monthly_delta": "0.5",
                "ratings_history": [
                    {
                        "begin_at": "2020-02-24T03:00:00+03:00",
                        "end_at": "2020-03-02T03:00:00+03:00",
                        "rating": 4.3
                    },
                    {
                        "begin_at": "2020-03-02T03:00:00+03:00",
                        "end_at": "2020-03-09T03:00:00+03:00",
                        "rating": 4.1
                    },
                    {
                        "begin_at": "2020-03-09T03:00:00+03:00",
                        "end_at": "2020-03-16T03:00:00+03:00",
                        "rating": 4.5
                    },
                    {
                        "begin_at": "2020-03-16T03:00:00+03:00",
                        "end_at": "2020-03-23T03:00:00+03:00",
                        "rating": 4.9
                    },
                    {
                        "begin_at": "2020-03-23T03:00:00+03:00",
                        "end_at": "2020-03-30T03:00:00+03:00",
                        "rating": 4.8
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
    is_ratings_history_calculated
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
    'req_no_ratings',
    '2',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP,
    'license_pd_id2',
    'done',
    NULL,
    TRUE
)
;
