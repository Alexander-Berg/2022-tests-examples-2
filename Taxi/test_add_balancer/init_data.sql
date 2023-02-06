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
    '__DEFAULT_TEST__',
    '__DEFAULT_STABLE__',
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
)
;

insert into
    clownductor.parameters(
        subsystem_name,
        service_id,
        branch_id,
        service_values,
        remote_values
    )
values (
    'service_info',
    1,
    1,
    '{"network": "__ELRUSSO_STABLE"}'::jsonb,
    '{"network": "__ELRUSSO_STABLE"}'::jsonb
)
;
