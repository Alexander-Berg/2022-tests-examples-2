insert into
    task_processor.providers
    (name, tvm_id, hostname, tvm_name, updated_at)
values
    ('clownductor', 1234, '$mockserver/provider-client', 'clownductor', extract (epoch from now())),
    ('deoevgen', 1234, '$mockserver/provider-client', 'deoevgen', extract (epoch from now()))
;


insert into
    task_processor.cubes
    (name, provider_id, updated_at, needed_parameters, optional_parameters, invalid)
values
    ('testCube', 1, extract (epoch from now()), '["service_id", "job_id"]', '["env", "ticket"]'::jsonb, false),
    ('CubeNoOptional', 2, extract (epoch from now()), '["token"]', '[]'::jsonb, false),
    ('testCube3', 1, extract (epoch from now()), '["service_id", "job_id"]', '["env", "ticket"]'::jsonb, false),
    ('testCube4', 2, extract (epoch from now()), '["service_id", "job_id"]', '["env", "ticket"]'::jsonb, false),
    ('testCube5', 1, extract (epoch from now()), '["service_id", "job_id"]', '["env", "ticket"]'::jsonb, false)

;

insert into
    task_processor.recipes
    (name, provider_id, updated_at, job_vars, version)
values
    ('recipe_1', 1, extract (epoch from now()), '[]'::jsonb, 1),
    ('recipe_2', 2, extract (epoch from now()), '[]'::jsonb, 2),
    ('both', 1, extract (epoch from now()), '["var1", "var3"]'::jsonb, 1),
    ('both', 2, extract (epoch from now()), '["var2"]'::jsonb, 1)
;

insert into
    task_processor.stages
    (recipe_id, cube_id, updated_at, next_id)
values
    (1, 1, extract (epoch from now()), 3),
    (2, 2, extract (epoch from now()), null),
    (1, 2, extract (epoch from now()), null)
;

insert into task_processor.jobs (
    recipe_id,
    name,
    initiator,
    idempotency_token,
    change_doc_id,
    status
)
values
    (1, 'job_1', 'elrusso', 'token_1', 'test_change_doc_id_1', 'success'),
    (1, 'job_2', 'elrusso', 'token_2', 'test_change_doc_id_2', 'in_progress'),
    (2, 'job_3', 'elrusso', 'token_3', 'test_change_doc_id_3', 'inited'),
    (2, 'job_4', 'elrusso', 'token_4', 'test_change_doc_id_4', 'failed'),
    (2, 'job_5', 'elrusso', 'token_5', 'test_change_doc_id_1', 'in_progress'),
    (2, 'job_6', 'elrusso', 'token_6', 'test_change_doc_id_5', 'in_progress')
;
