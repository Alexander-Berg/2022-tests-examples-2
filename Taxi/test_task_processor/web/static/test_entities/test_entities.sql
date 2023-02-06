insert into
    task_processor.providers
    (name, tvm_id, hostname, tvm_name, updated_at)
values
    ('elrusso', 234, 'http://taxi.yandex.net', 'tvm_name', extract (epoch from now()));


insert into
    task_processor.recipes
    (name, updated_at, job_vars, provider_id)
values
    (
        'test recipe',
         extract (epoch from now()),
        '["service_id", "test", "env", "new_service_ticket"]'::jsonb,
        1
    )
;


insert into task_processor.jobs (
    recipe_id,
    name,
    initiator,
    idempotency_token,
    change_doc_id,
    created_at
)
values
    (1, 'job_1', 'elrusso', 100, 'test_change_doc_id_1', 1586267052),
    (1, 'job_2', 'elrusso', 101, 'test_change_doc_id_2', 1586269052)
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
    ('100', 2, 1),
    ('101', 1, 1),
    ('101', 2, 1),
    ('5', 2, 2),
    ('1', 2, 2),
    ('1', 1, 2),
    ('1', 1, 1);
