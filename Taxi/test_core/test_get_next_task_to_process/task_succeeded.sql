INSERT INTO task_processor.tasks (job_id, cube_id, name, status)
VALUES (1, 1, 'a', 'in_progress'),
       (1, 1, 'b', 'success'),
       (1, 1, 'c', 'in_progress')
;


INSERT INTO task_processor.task_deps (prev_task_id, next_task_id)
VALUES (1, 2),
       (2, 3)
;
