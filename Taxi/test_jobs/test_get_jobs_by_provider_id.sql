insert into
    task_processor.providers
    (name, tvm_id, hostname, tvm_name, updated_at)
values
    ('deoevgen', 1234, 'http://taxi.yandex.net', 'tvm_name', extract (epoch from now()))
;


insert into
    task_processor.recipes
    (name, updated_at, job_vars, provider_id)
values
    (
        'test_create_job',
         extract (epoch from now()),
        '["service_id", "test", "env", "new_service_ticket"]'::jsonb,
        1
    )
;

insert into
    task_processor.cubes
    (name, provider_id, updated_at, needed_parameters, optional_parameters, invalid)
values
    ('CubeDeploy1',1, extract (epoch from now()), '["service_id", "test"]', '["env", "ticket"]'::jsonb, false),
    ('CubeDeploy2',1, extract (epoch from now()), '["service_id", "test"]', '["env", "ticket"]'::jsonb, false),
    ('CubeDeploy3',1, extract (epoch from now()), '["service_id", "test"]', '["env", "ticket"]'::jsonb, false),
    ('CubeDeploy4',1, extract (epoch from now()), '["service_id", "test"]', '["env", "ticket"]'::jsonb, false),
    ('CubeDeploy5',1, extract (epoch from now()), '["service_id", "test"]', '["env", "ticket"]'::jsonb, false)
;

insert into
    task_processor.stages
    (next_id, recipe_id, cube_id, updated_at, input)
 values
    (null, 1, 1, 1579791016, '{"test_input_data": "service_id"}'),
    (1, 1, 2, 1579791016, '{}'),
    (2, 1, 3, 1579791016, '{}'),
    (3, 1, 4, 1579791016, '{}'),
    (4, 1, 5, 1579791016, '{}')
;
