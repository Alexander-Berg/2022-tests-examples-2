INSERT INTO takeout.jobs
    (job_id, uid, created_at, updated_at)
VALUES
    ('job_id_uid_not_found', 'uid_not_found', NOW(), NOW()),
    ('job_id_portal_user', 'portal_user', NOW(), NOW())
ON CONFLICT DO NOTHING;
