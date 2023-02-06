insert into
    task_processor.providers
    (name, tvm_id, updated_at, hostname, tvm_name)
values
    ('deoevgen', 1234, extract (epoch from now()), '$mockserver/provider-client', 'deoevgen');


insert into
    task_processor.recipes
    (name, updated_at, job_vars, provider_id)
values
    (
        'test_create_job',
         extract (epoch from now()),
        '["service_id", "test", "env", "new_service_ticket"]'::jsonb,
        1
    ),
    (
        'test_failed_job',
        extract (epoch from now()),
        '["service_id", "test", "env", "new_service_ticket"]'::jsonb,
        1
    )
;

insert into
    task_processor.cubes
    (name, provider_id, updated_at, needed_parameters, optional_parameters)
values
    ('CubeDeploy1',1, extract (epoch from now()), '["service_id", "test"]', '["env", "ticket"]'::jsonb),
    ('CubeDeploy2',1, extract (epoch from now()), '["service_id", "test"]', '["env", "ticket"]'::jsonb),
    ('CubeDeploy3',1, extract (epoch from now()), '["service_id", "test"]', '["env", "ticket"]'::jsonb),
    ('CubeDeploy4',1, extract (epoch from now()), '["service_id", "test"]', '["env", "ticket"]'::jsonb),
    ('CubeDeploy5',1, extract (epoch from now()), '["service_id", "test"]', '["env", "ticket"]'::jsonb),
    ('CubeDeployFailed',1, extract (epoch from now()), '["service_id", "test"]', '["env", "ticket"]'::jsonb)
;

insert into
    task_processor.stages
    (next_id, recipe_id, cube_id, updated_at, input)
 values
    (null, 1, 1, 1579791016, '{"test_input_data": "service_id"}'),
    (1, 1, 2, 1579791016, '{}'),
    (2, 1, 3, 1579791016, '{}'),
    (3, 1, 4, 1579791016, '{}'),
    (2, 1, 5, 1579791016, '{}'),
    (null, 2, 6, 1579791016, '{}')
;

update
    task_processor.stages
set
    next_id=5
where
    id=3
;
