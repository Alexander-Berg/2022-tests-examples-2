INSERT INTO task_manager.tasks (id, job_id, name, input_mapping, output_mapping)
VALUES (1, 1, 'a', '{}', '{}'),
       (2, 1, 'a', '{}', '{}')
;

INSERT INTO task_manager.task_deps (prev_task_id, next_task_id)
VALUES (1, 2)
;
