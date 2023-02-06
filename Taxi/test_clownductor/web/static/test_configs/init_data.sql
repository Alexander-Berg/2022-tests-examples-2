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

insert into clownductor.configs (
    branch_id,
    name,
    plugins,
    libraries,
    is_service_yaml
)
values
(2, 'EXIST_CONFIG', '{plugin}', '{lib}', True),
(2, 'EXIST_CONFIGS', '{plugin}', '{lib}', True),
(1, 'CONFIG_1', '{}', '{lib_1}', False),
(1, 'CONFIG_2', '{}', '{lib_1, lib_2}', True),
(1, 'CONFIG_3', '{plugin_1}', '{lib_1, lib_2}', True),
(1, 'CONFIG_4', '{plugin_2}', '{lib_3}', True),
(1, 'CONFIG_5', '{plugin_2}', '{lib_3}', True)
;
