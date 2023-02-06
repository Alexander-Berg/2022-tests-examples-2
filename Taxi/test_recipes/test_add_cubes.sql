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
    ('testCube',2, extract (epoch from now()), '["service_id", "job_id"]', '["env", "ticket"]'::jsonb, false),
    ('CubeNoOptional',2, extract (epoch from now()), '["token"]', '[]'::jsonb, false),
    ('CubeNoOptional',1, extract (epoch from now()), '["token"]', '[]'::jsonb, false)
;

insert into
    task_processor.recipes
    (name, provider_id, updated_at, job_vars, version)
values
    ('already_exist_recipe',2, extract (epoch from now()), '[]'::jsonb, 1),
    ('already_exist_recipe',2, extract (epoch from now()), '[]'::jsonb, 2),
    ('new_meta',2, extract (epoch from now()), '[]'::jsonb, 1)
;

insert into
    task_processor.stages
    (recipe_id, cube_id, updated_at)
values
    (1, 1, extract (epoch from now())),
    (2, 1, extract (epoch from now())),
    (3, 3, extract (epoch from now())),
    (3, 2, extract (epoch from now())),
    (3, 1, extract (epoch from now()))
;
