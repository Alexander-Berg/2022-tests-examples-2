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
    'extra_super_check_id1',
    'extra_super_idempotency_token1',
    '2020-07-01 10:00:00.000000+03',
    '2020-07-01 10:00:00.000000+03',
    'extra_super_driver_license_pd1',
    'done'
),
(
    'park1',
    'extra_super_check_id2',
    'extra_super_idempotency_token2',
    '2020-07-03 10:00:00.000000+03',
    '2020-07-03 10:00:00.000000+03',
    'extra_super_driver_license_pd1',
    'internal_error'
),
(
    'park1',
    'extra_super_check_id3',
    'extra_super_idempotency_token3',
    '2020-07-06 10:00:00.000000+03',
    '2020-07-06 10:00:00.000000+03',
    'extra_super_driver_license_pd1',
    'pending'
),
(
    'park1',
    'extra_super_check_id4',
    'extra_super_idempotency_token4',
    '2020-07-01 10:00:00.000000+03',
    '2020-07-01 10:00:00.000000+03',
    'extra_super_driver_license_pd2',
    'done'
),
(
    'park1',
    'extra_super_check_id5',
    'extra_super_idempotency_token5',
    '2020-07-03 10:00:00.000000+03',
    '2020-07-03 10:00:00.000000+03',
    'extra_super_driver_license_pd2',
    'done'
)
;
