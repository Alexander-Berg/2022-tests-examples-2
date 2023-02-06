insert into clownductor.namespaces (name) values ('taxi');

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
    '{"logins": ["project_login_11"]}'::jsonb,
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
),
(
    1,
    'test-db-service',
    'artifact_name',
    'postgres',
    'unit_test',
    'abc_service'
),
(
    1,
    'separate-test-db-service',
    'artifact_name',
    'postgres',
    'unit_test',
    'another_abc_service'
),
(
    1,
    'test-service-4',
    'artifact_name',
    'nanny',
    'unit_test',
    'abc_service_4'
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
),
(
    1,
    'testing_branch',
    'testing',
    'test-service-1-direct-testing'
),
(
    4,
    'stable',
    'stable',
    'test-service-4-direct'
)
;
