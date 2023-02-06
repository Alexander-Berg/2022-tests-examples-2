INSERT INTO fleet_drivers_scoring.checks
(
    park_id,
    check_id,
    idempotency_token,
    created_at,
    updated_at,
    license_pd_id,
    status
)
VALUES
(
    'park1',
    'req_done',
    '1',
    '2020-07-25 10:00:0.000000+00',
    '2020-07-25 10:00:0.000000+00',
    'license_pd_id',
    'done'
)
