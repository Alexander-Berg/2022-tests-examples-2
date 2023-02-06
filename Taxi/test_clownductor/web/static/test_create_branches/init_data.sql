insert into clownductor.namespaces (name) values ('test');

insert into
    clownductor.projects (
        name,
        network_testing,
        network_stable,
        service_abc,
        yp_quota_abc,
        tvm_root_abc,
        owners,
        namespace_id
    )
values (
    'test_project',
    '_taxitestnets_',
    '_hwtaxinets_',
    'taxiservicesdeploymanagement',
    'taxiquotaypdefault',
    'taxitvmaccess',
    '{"logins": ["project_login_11"], "groups": ["meow"]}'::jsonb,
    1
)
;

insert into
    clownductor.services (
        project_id,
        name,
        artifact_name,
        cluster_type,
        requester,
        abc_service
    )
values (
    1,
    'test-service',
    'artifact_name',
    'nanny',
    'unit_test',
    'abc_service'
), (
    1,
    'test-service-2',
    'artifact_name',
    'conductor',
    'unit_test',
    'abc_service'
), (
    1,
    'test-service-3',
    'artifact_name',
    'postgres',
    'unit_test',
    'abc_service'
), (
    1,
    'test-service-4',
    'artifact_name',
    'mongo_mdb',
    'unit_test',
    'abc_service'
), (
    1,
    'test-service-5',
    'artifact_name',
    'redis_mdb',
    'unit_test',
    'abc_service'
)
;

insert into
    clownductor.branches (
        service_id,
        name,
        env,
        direct_link
    )
values (
    1,
    'stable_branch',
    'stable',
    'test-service-1-direct'
), (
    1,
    'testing_branch',
    'testing',
    'test-service-1-direct-testing'
), (
    3,
    'db-branch',
    'testing',
    'db-link'
), (
    4,
    'db-branch',
    'testing',
    'db-link'
), (
    5,
    'db-branch',
    'testing',
    'db-link'
)
;


insert into clownductor.parameters (
    subsystem_name,
    service_id,
    branch_id,
    service_values,
    remote_values
)
values
    (
        'nanny', 1, 1,
        '{}'::jsonb,
        '{"cpu": 3500, "ram": 7000, "root_size": 10240, "work_dir": 512, "instances": 2, "datacenters_count": 2, "persistent_volumes": [{"size": 10240, "path": "/logs", "type": "hdd"}]}'::jsonb
    );

