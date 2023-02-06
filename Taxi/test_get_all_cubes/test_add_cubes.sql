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
    ('CubeNoOptional',2, extract (epoch from now()), '["token"]', '[]'::jsonb, false)
;
