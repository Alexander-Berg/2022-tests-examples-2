INSERT INTO takeout.jobs
    (job_id, uid, status, service_name)
VALUES
    ('1', '2', 'pending', 'a'),
    ('2', '3', 'pending', 'b'),
    ('3', '3', 'pending', 'c'),
    ('4', '3', 'done', 'v')
ON CONFLICT DO NOTHING;
