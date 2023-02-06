insert into
    task_processor.providers
    (name, tvm_id, hostname, tvm_name, updated_at)
values
    ('vstimchenko', 1234, 'http://taxi.yandex.net', 'tvm_name', extract (epoch from now() - INTERVAL '24 HOURS'));


insert into
    task_processor.recipes
    (name, updated_at, job_vars, provider_id)
values
    (
        'test_create_job_recipe',
         EXTRACT(EPOCH FROM NOW() - INTERVAL '30 MINUTES'),
        '["service_id", "test", "env", "new_service_ticket"]'::jsonb,
        1
    ),
    (
        'test_failed_job_recipe',
         EXTRACT(EPOCH FROM NOW() - INTERVAL '30 MINUTES'),
        '["service_id", "test", "env", "new_service_ticket"]'::jsonb,
        1
    ),
    (
        'test_invalid_job_recipe',
         EXTRACT(EPOCH FROM NOW() - INTERVAL '30 MINUTES'),
        '["service_id", "test", "env", "new_service_ticket"]'::jsonb,
        1
    )
;

insert into
    task_processor.cubes
    (name, provider_id, updated_at, needed_parameters, optional_parameters, invalid)
values
    ('CubeDeploy1',1, EXTRACT(EPOCH FROM NOW() - INTERVAL '20 MINUTES'), '["service_id", "test"]', '["env", "ticket"]'::jsonb, false),
    ('CubeDeploy2',1, EXTRACT(EPOCH FROM NOW() - INTERVAL '20 MINUTES'), '["service_id", "test"]', '["env", "ticket"]'::jsonb, false),
    ('CubeDeploy3',1, EXTRACT(EPOCH FROM NOW() - INTERVAL '20 MINUTES'), '["service_id", "test"]', '["env", "ticket"]'::jsonb, true),
    ('CubeDeploy4',1, EXTRACT(EPOCH FROM NOW() - INTERVAL '20 MINUTES'), '["service_id", "test"]', '["env", "ticket"]'::jsonb, false),
    ('CubeDeploy5',1, EXTRACT(EPOCH FROM NOW() - INTERVAL '20 MINUTES'), '["service_id", "test"]', '["env", "ticket"]'::jsonb, false)
;

insert into
    task_processor.stages
    (next_id, recipe_id, cube_id, updated_at, input)
 values
    (null, 1, 1, EXTRACT(EPOCH FROM NOW() - INTERVAL '20 MINUTES'), '{"test_input_data": "service_id"}'),
    (1, 1, 2, EXTRACT(EPOCH FROM NOW() - INTERVAL '20 MINUTES'), '{}'),
    (2, 1, 3, EXTRACT(EPOCH FROM NOW() - INTERVAL '20 MINUTES'), '{}'),
    (3, 1, 4, EXTRACT(EPOCH FROM NOW() - INTERVAL '20 MINUTES'), '{}'),
    (2, 1, 5, EXTRACT(EPOCH FROM NOW() - INTERVAL '20 MINUTES'), '{}')
;

update
    task_processor.stages
set
    next_id=5
where
    id=3
;

insert into task_processor.jobs (
    recipe_id,
    name,
    initiator,
    idempotency_token,
    change_doc_id,
    created_at,
    finished_at,
    status,
    real_time,
    total_time
)
values (
    1,
    'job1',
    'deoevgen',
    12345,
    'test_change_doc_id_1',
    EXTRACT(EPOCH FROM NOW() - INTERVAL '12 MINUTES'),
    EXTRACT(EPOCH FROM NOW() - INTERVAL '11 MINUTES'),
    'success',
    1,
    1
),
(
    1,
    'job2',
    'deoevgen',
    12346,
    'test_change_doc_id_2',
    EXTRACT(EPOCH FROM NOW() - INTERVAL '12 MINUTES'),
    EXTRACT(EPOCH FROM NOW() - INTERVAL '11 MINUTES'),
    'failed',
    1,
    1
),
(
    1,
    'job3',
    'deoevgen',
    12347,
    'test_change_doc_id_3',
    EXTRACT(EPOCH FROM NOW() - INTERVAL '12 MINUTES'),
    NULL,
    'in_progress',
    1,
    1
)
;

insert into task_processor.job_variables (
    job_id,
    variables
)
values (1, '{}')
;

insert into task_processor.tasks(
    job_id,
    cube_id,
    name,
    created_at,
    status,
    updated_at,
    real_time,
    total_time
)
values
(
    1,
    1,
    'CubeDeploy1',
    EXTRACT(EPOCH FROM NOW() - INTERVAL '20 MINUTES'),
    'success',
    EXTRACT(EPOCH FROM NOW() - INTERVAL '17 MINUTES'),
    1,
    1
),
(
    1,
    2,
    'CubeDeploy2',
    EXTRACT(EPOCH FROM NOW() - INTERVAL '17 MINUTES'),
    'success',
    EXTRACT(EPOCH FROM NOW() - INTERVAL '12 MINUTES'),
    1,
    1
),
(
    2,
    1,
    'CubeDeploy1',
    EXTRACT(EPOCH FROM NOW() - INTERVAL '20 MINUTES'),
    'success',
    EXTRACT(EPOCH FROM NOW() - INTERVAL '17 MINUTES'),
    1,
    1
),
(
    2,
    2,
    'CubeDeploy2',
    EXTRACT(EPOCH FROM NOW() - INTERVAL '17 MINUTES'),
    'failed',
    EXTRACT(EPOCH FROM NOW() - INTERVAL '11 MINUTES'),
    1,
    1
),
(
    3,
    1,
    'CubeDeploy1',
    EXTRACT(EPOCH FROM NOW() - INTERVAL '20 MINUTES'),
    'success',
    EXTRACT(EPOCH FROM NOW() - INTERVAL '17 MINUTES'),
    1,
    1
),
(
    3,
    2,
    'CubeDeploy2',
    EXTRACT(EPOCH FROM NOW() - INTERVAL '17 MINUTES'),
    'in_progress',
    NULL,
    1,
    1
)
;
