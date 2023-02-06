insert into
    perforator.services (tvm_name, clown_id, project_id)
values
    ('existed_tvm_service', 1, 1),
    ('envoy-exp-bravo', 4, 2)
;

insert into
    perforator.environments (service_id, tvm_id, env_type)
values
    (1, 1, 'production'),
    (2, 2023814, 'production')
;

insert into
    perforator.environment_rules (source_env_id, destination_env_id)
values
    (1, 1)
;
