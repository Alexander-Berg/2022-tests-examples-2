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
    '{"logins": ["elrusso"], "groups": ["elrusoo_group"]}'::jsonb,
    1
),
(
    'lavka',
    '_taxitestnets_',
    '_hwtaxinets_',
    'taxiservicesdeploymanagement',
    'taxiquotaypdefault',
    'taxitvmaccess',
    '{"logins": ["elrusso"], "groups": ["elrusoo_group"]}'::jsonb,
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
    'elrusso-service',
    'artifact_name',
    'nanny',
    'unit_test',
    'abc_service'
),
(
    1,
    'test-dev-service',
    'artifact_name-dev',
    'nanny',
    'unit_test',
    'abc_service'
),
(
    2,
    'uncommon-service',
    'artifact_name-dev',
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
        direct_link,
        artifact_version
    )
values (
    1,
    'stable_branch',
    'stable',
    'test-service-1-direct',
    ''
), (
    1,
    'testing_branch',
    'testing',
    'test-service-1-direct-testing',
    ''
), (
    3,
    'testing_branch_wrong',
    'testing',
    'test-service-3-dev-removal-testing-right',
    ''
), (
    3,
    'dev-branch',
    'unstable',
    'test-service-3-dev-removal-testing-right',
    ''
),
(
    4,
    'dev-branch',
    'testing',
    'test-service-4-dev-removal-testing-right',
    ''
)
;

insert into
    clownductor.parameters(
        subsystem_name,
        service_id,
        branch_id,
        service_values,
        remote_values,
        updated_at
    )
values (
    'nanny',
    1,
    2,
    '{"cpu": 1000, "ram": 2048, "work_dir": 256, "instances": 2, "root_size": 10240, "datacenters_count": 2, "persistent_volumes": [{"path": "/cores", "size": 10240, "type": "hdd"}, {"path": "/logs", "size": 50000, "type": "hdd"}, {"path": "/var/cache/yandex", "size": 2048, "type": "hdd"}]}'::jsonb,
    '{"cpu": 500, "ram": 2048, "work_dir": 256, "instances": 2, "root_size": 10240, "persistent_volumes": [{"path": "/cores", "size": 10240, "type": "hdd"}, {"path": "/logs", "size": 31200, "type": "hdd"}]}'::jsonb,
    extract(epoch from now())::int
), (
    'nanny',
    3,
    3,
    '{"cpu": 1000, "ram": 2048, "work_dir": 256, "instances": 2, "root_size": 10240, "datacenters_count": 2, "persistent_volumes": [{"path": "/cores", "size": 10240, "type": "hdd"}, {"path": "/logs", "size": 50000, "type": "hdd"}, {"path": "/var/cache/yandex", "size": 2048, "type": "hdd"}]}'::jsonb,
    '{"cpu": 500, "ram": 2048, "instances": 2, "persistent_volumes": [{"path": "/cores", "size": 10240, "type": "hdd"}, {"path": "/logs", "size": 31200, "type": "hdd"}]}'::jsonb,
    extract(epoch from now())::int

), (
    'nanny',
    3,
    4,
    '{"root_bandwidth_guarantee_mb_per_sec": 1, "cpu": 1000, "ram": 2048, "work_dir": 256, "instances": 2, "root_size": 10240, "datacenters_count": 2, "persistent_volumes": [{"path": "/cores", "size": 10240, "type": "hdd"}, {"path": "/logs", "size": 50000, "type": "hdd"}, {"path": "/var/cache/yandex", "size": 2048, "type": "hdd"}]}'::jsonb,
    '{"root_bandwidth_guarantee_mb_per_sec": 1, "cpu": 500, "ram": 2048, "instances": 2, "persistent_volumes": [{"path": "/cores", "size": 10240, "type": "hdd"}, {"path": "/logs", "size": 31200, "type": "hdd"}]}'::jsonb,
    extract(epoch from now())::int

);



insert into task_manager.jobs (
    service_id,
    branch_id,
    name,
    initiator,
    status
)
values (
    1,
    1,
    'DeployNannyServiceNoApprove',
    'deoevgen',
    'canceled'
);
