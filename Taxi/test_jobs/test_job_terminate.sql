insert into
    task_processor.providers
    (name, tvm_id, hostname, tvm_name, updated_at)
values
    ('clownductor', 1234, '$mockserver/provider-client', 'clownductor', extract (epoch from now())),
    ('deoevgen', 1234, '$mockserver/provider-client', 'deoevgen', extract (epoch from now()))
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
    task_processor.recipes
    (name, provider_id, updated_at, job_vars, version)
values
    ('already_exist_recipe',2, extract (epoch from now()), '[]'::jsonb, 1),
    ('already_exist_recipe',2, extract (epoch from now()), '[]'::jsonb, 2)
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
    (null, 2, 1, 1579791016, '{"test_input_data": "service_id"}'),
    (6, 2, 2, 1579791016, '{}'),
    (7, 2, 3, 1579791016, '{}'),
    (8, 2, 4, 1579791016, '{}'),
    (9, 2, 5, 1579791016, '{}')
;
