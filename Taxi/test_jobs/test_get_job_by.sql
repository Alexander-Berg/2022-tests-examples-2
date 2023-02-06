insert into
    task_processor.providers
    (name, tvm_id, hostname, tvm_name, updated_at)
values
    ('clownductor', 1234, '$mockserver/provider-client', 'clownductor', extract (epoch from now())),
    ('deoevgen', 1234, '$mockserver/provider-client', 'deoevgen', extract (epoch from now()))
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

insert into task_processor.jobs (
    recipe_id,
    name,
    initiator,
    idempotency_token,
    change_doc_id,
    status,
    created_at,
    finished_at
)
values
    (1, 'job_1', 'elrusso', 'token_1', 'test_change_doc_id_1', 'success', 1628266318, 1628266400),
    (1, 'job_2', 'elrusso', 'token_2', 'test_change_doc_id_2', 'in_progress', 1628266318, 1628266400),
    (2, 'job_3', 'elrusso', 'token_3', 'test_change_doc_id_3', 'inited', 1628266318, 1628266319),
    (2, 'job_4', 'elrusso', 'token_4', 'test_change_doc_id_4', 'failed', 1628266318, 1628266366),
    (2, 'job_4', 'elrusso', 'token_5', 'test_change_doc_id_1', 'in_progress', 1628266318, 1628266400),
    (2, 'job_6', 'elrusso', 'token_6', 'test_change_doc_id_5', 'in_progress', 1628266318, 1628266800),
    (2, 'job_4', 'elrusso', 'token_7', 'test_change_doc_id_4', 'failed', 1628266318, 1628266366)
;


insert into task_processor.job_variables (
    job_id,
    variables
)
values
(1, '{}'),
(2, '{"a": 1}'),
(3, '{}'),
(4, '{}'),
(5, '{}'),
(6, '{}')
;


insert into
    task_processor.entity_types
    (entity_type)
values
    ('service'),
    ('branch'),
    ('project');

insert into
    task_processor.external_entities_links
    (external_id, entity_type_id, job_id)
values
    ('100', 1, 1),
    ('100', 1, 2),
    ('100', 1, 7),
    ('100', 2, 1),
    ('101', 1, 4),
    ('102', 1, 5),
    ('103', 1, 6),
    ('100', 1, 4);
