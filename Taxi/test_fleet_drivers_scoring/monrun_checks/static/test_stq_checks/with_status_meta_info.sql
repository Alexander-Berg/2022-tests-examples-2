WITH input(token, status, status_meta_info, time) AS (
    VALUES ('id1', 'failed', '{"reason": "not_enough_money"}', '2020-05-17T10:00+00'),
           ('id2', 'failed', '{"reason": "nothing_changed"}', '2020-05-17T10:00+00'),
           ('id3', 'done', NULL, '2020-05-17T10:00+00')
)
INSERT
INTO fleet_drivers_scoring.checks(park_id, check_id, idempotency_token, created_at, updated_at, status, status_meta_info, license_pd_id)
SELECT 'park_id', token, token, time::TIMESTAMPTZ, time::TIMESTAMPTZ, status::fleet_drivers_scoring.check_status, status_meta_info::jsonb, 'license_pd_id'
FROM input;
