insert into
    perforator.services (tvm_name, clown_id, project_id)
values
    ('existed_tvm_service', 123, 1),
    ('existed_tvm_service_2', null, null),
    ('existed_tvm_service_3', 124, 1),
    ('existed_tvm_service_4', null, null),
    ('empty_service', null, null)
;

insert into
    perforator.environments (service_id, tvm_id, env_type)
values
    (1, 1000, 'unstable'),
    (1, 1000, 'testing'),
    (1, 1002, 'production'),
    (2, 2000, 'production'),
    (2, 2002, 'testing'),
    (3, 3000, 'unstable'),
    (3, 3000, 'testing'),
    (3, 3002, 'production'),
    (4, 4000, 'production'),
    (4, 4002, 'testing')
;

insert into
    perforator.environment_rules (source_env_id, destination_env_id)
values
    (2, 5),
    (3, 3)
;
