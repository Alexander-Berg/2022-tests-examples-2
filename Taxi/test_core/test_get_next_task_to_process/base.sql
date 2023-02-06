INSERT INTO task_processor.providers (name, tvm_id, updated_at, hostname, tvm_name)
VALUES ('A', 123, 0, '', '')
;

INSERT INTO task_processor.cubes (name, provider_id, updated_at)
VALUES ('A', 1, 0)
;

INSERT INTO task_processor.recipes (name, provider_id, updated_at)
VALUES ('A', 1, 0)
;

INSERT INTO task_processor.jobs (name, recipe_id, change_doc_id)
VALUES ('A', 1, '')
;
