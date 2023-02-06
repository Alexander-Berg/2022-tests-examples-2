INSERT INTO task_processor.recipes (name, provider_id, job_vars, version)
VALUES ('A', 1, '[]'::jsonb, 1);

INSERT INTO task_processor.stages (recipe_id, cube_id)
VALUES (1, 1);
