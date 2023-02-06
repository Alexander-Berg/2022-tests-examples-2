INSERT INTO integration_tasks
    (id, place_id, type, status, created_at)
VALUES
    ('task_id__1', 'place_id__1', 'price', 'created', now() - interval '310 seconds'),
    ('task_id__2', 'place_id__1', 'price', 'created', now())
;
