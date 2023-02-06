insert into
    task_processor.providers
    (name, tvm_id, hostname, tvm_name, updated_at)
values
    ('clownductor', 1234, '$mockserver/provider-client', 'clownductor', extract (epoch from now()));


insert into
    task_processor.recipes
    (name, updated_at, job_vars, provider_id)
values
    (
        'test_abc_cube',
         extract (epoch from now()),
        '[]'::jsonb,
        1
    )
;

insert into
    task_processor.cubes
    (name, provider_id, updated_at, needed_parameters, optional_parameters, invalid, output_parameters)
values
    ('AbcCubeGenerateServiceName',1, extract (epoch from now()), '["project", "service", "st_task"]', '[]'::jsonb, false, '["name", "slug"]'::jsonb)
;

insert into
    task_processor.stages
    (next_id, recipe_id, cube_id, updated_at, input, output)
 values
    (null, 1, 1, 1579791016, '{}', '{"service_abc_name": "name", "service_abc_slug": "slug"}')
;
