insert into
    perforator.services_warranty (
        tvm_name,
        env_type,
        tvm_id,
        action,
        ensured,
        attempts
    )
values
    ('existed_tvm_service', 'testing', 1001, 'edit', false, 0),
    ('existed_tvm_service', 'production', null, 'delete', false, 0),
    ('existed_tvm_service_7', 'production', 7000, 'create', false, 0),
    ('existed_tvm_service_3', 'production', 3000, 'create', false, 0)
;


insert into
    perforator.rules_warranty (
        source,
        destination,
        env_type,
        action,
        ensured,
        attempts
    )
values
    ('meow_service', 'some_service', 'testing', 'create', false, 0),
    ('existed_tvm_service', 'existed_tvm_service_2', 'production', 'create', false, 0),
    ('existed_tvm_service', 'existed_tvm_service', 'production', 'delete', false, 0)
;

