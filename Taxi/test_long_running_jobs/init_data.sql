INSERT INTO task_processor.providers (id, name, tvm_id, created_at, updated_at, hostname, tvm_name)
VALUES (1, 'Dummy provider #1', 1, 911549700, 911549700, 'http://dummy1.taxi.tst.yandex.ru', 'dummy tvm #1'),
       (2, 'Dummy provider #2', 2, 911549760, 911549760, 'http://dummy2.taxi.tst.yandex.ru', 'dummy tvm #2')
;

INSERT INTO task_processor.recipes (id, name, provider_id, created_at, updated_at, job_vars, version)
VALUES (1, 'Dummy recipe #1', 1, 911636100, 911636100, '["service_id", "new_project_id"]'::jsonb, 1),
       (2, 'Dummy recipe #2', 1, 911636160, 911636160, '["service_id", "new_project_id"]'::jsonb, 1),
       (3, 'Dummy recipe #3', 1, 911636220, 911636220, '["service_id", "new_project_id"]'::jsonb, 1),
       (4, 'Dummy recipe #4', 2, 911636280, 911636280, '["service_id", "new_project_id"]'::jsonb, 1),
       (5, 'Dummy recipe #5', 2, 911636340, 911636340, '["service_id", "new_project_id"]'::jsonb, 1)
;

INSERT INTO task_processor.jobs (id, name, recipe_id, created_at, status, change_doc_id)
VALUES (1, 'Dummy job #1', 1, 911722500, 'in_progress', 'dummy change #1'),
       (2, 'Dummy job #1', 1, 911722560, 'success', 'dummy change #2'),
       (3, 'Dummy job #1', 1, 911722620, 'success', 'dummy change #3'),
       (4, 'Dummy job #2', 2, 911722680, 'in_progress', 'dummy change #4'),
       (5, 'Dummy job #2', 2, 911722740, 'failed', 'dummy change #5'),
       (6, 'Dummy job #2', 2, 911722800, 'in_progress', 'dummy change #6'),
       (7, 'Dummy job #2', 2, 911722860, 'canceled', 'dummy change #7'),
       (8, 'Dummy job #2', 2, 911722920, 'canceled', 'dummy change #8'),
       (9, 'Dummy job #2', 3, 911722980, 'in_progress', 'dummy change #9'),
       (10, 'Dummy job #2', 3, 911723040, 'success', 'dummy change #10'),
       (11, 'Dummy job #3', 4, 911723100, 'success', 'dummy change #11'),
       (12, 'Dummy job #3', 4, 911731160, 'in_progress', 'dummy change #12'),
       (13, 'Dummy job #3', 4, 911723160, 'success', 'dummy change #13'),
       (14, 'Dummy job #3', 4, 911723220, 'failed', 'dummy change #14'),
       (15, 'Dummy job #3', 4, 911723280, 'success', 'dummy change #15'),
       (16, 'Dummy job #3', 5, 911723340, 'in_progress', 'dummy change #16'),
       (17, 'Dummy job #3', 5, 911723400, 'success', 'dummy change #17'),
       (18, 'Dummy job #3', 5, 911723460, 'failed', 'dummy change #18'),
       (19, 'Dummy job #3', 5, 911723520, 'canceled', 'dummy change #19'),
       (20, 'Dummy job #3', 5, 911723580, 'in_progress', 'dummy change #20')
;
