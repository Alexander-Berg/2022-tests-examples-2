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
    offer,
    discount_type
)
VALUES
(
    'park1',
    'check_id',
    '100000000',
    '2020-07-25 11:00:0.000000+00',
    '2020-07-25 11:00:0.000000+00',
    'license_pd_id',
    'pending',
    NULL,
    FALSE,
    '{
        "decision": {"can_buy": true},
        "price": {
            "amount": "1",
            "currency": "RUB"
        }
    }'::jsonb,
    NULL
),
(
    'park1',
    'req_done1',
    '1',
    '2020-07-25 10:00:0.000000+00',
    '2020-07-25 10:00:0.000000+00',
    'license_pd_id1',
    'done',
    NULL,
    FALSE,
    '{
        "decision": {"can_buy": true},
        "price": {
            "amount": "100",
            "currency": "RUB"
        }
    }'::jsonb,
    NULL
);
