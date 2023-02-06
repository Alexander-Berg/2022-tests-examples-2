INSERT INTO takeout.jobs
    (job_id, uid, created_at, updated_at)
VALUES
    ('portal_user', 'portal_user', NOW(), NOW())
ON CONFLICT DO NOTHING;
