INSERT INTO task_manager.tasks (id, job_id, name, input_mapping, output_mapping, status)
VALUES (1, 1, 'a', '{}', '{}', 'success'),
       (2, 1, 'a', '{}', '{}', 'in_progress')
;

INSERT INTO task_manager.task_deps (prev_task_id, next_task_id)
VALUES (1, 2)
;
