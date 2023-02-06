WITH input(token, status, time) AS (
    VALUES ('id1', 'internal_error', '2020-05-17T05:00+00'),
           ('id2', 'internal_error', '2020-05-17T05:00+00'),
           ('id3', 'internal_error', '2020-05-17T05:00+00'),
           ('id4', 'internal_error', '2020-05-17T05:00+00'),
           ('id5', 'done', '2020-05-17T10:00+00'),
           ('id6', 'done', '2020-05-17T10:00+00')
)
INSERT
INTO fleet_drivers_scoring.checks(park_id, check_id, idempotency_token, created_at, updated_at, status, license_pd_id)
SELECT 'park_id', token, token, time::TIMESTAMPTZ, time::TIMESTAMPTZ, status::fleet_drivers_scoring.check_status, 'license_pd_id'
FROM input;
