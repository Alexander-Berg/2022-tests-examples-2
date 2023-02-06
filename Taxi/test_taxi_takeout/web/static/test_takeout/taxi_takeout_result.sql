INSERT INTO takeout.jobs
    (job_id, uid,  service_name, status, result, created_at, updated_at)
VALUES
    ('job_id_found_pending', 'uid', 'ridehistory', 'pending', NULL, NOW(), NOW()),
    ('job_id_found_done', 'uid', 'ridehistory', 'done', NULL, NOW(), NOW()),
    ('job_id_not_found_service', 'uid', 'safety_center', 'pending', NULL, NOW(), NOW())
ON CONFLICT DO NOTHING;


INSERT INTO takeout.jobs
    (job_id, uid, service_name, status, result, created_at, updated_at)
VALUES
    ('job_id_found_with_result', 'uid', 'ridehistory', 'done', 'some_result', NOW() - INTERVAL '1 hour', NOW())
ON CONFLICT DO NOTHING;
