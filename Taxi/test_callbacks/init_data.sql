insert into clownductor.namespaces (name) values ('taxi');

insert into
    clownductor.projects (
        name,
        network_testing,
        network_stable,
        service_abc,
        yp_quota_abc,
        tvm_root_abc,
        namespace_id
    )
values (
    'test_project',
    '_TAXITESTNETS_',
    '_HWTAXINETS_',
    'taxiservicesdeploymanagement',
    'taxiquotaypdefault',
    'taxitvmaccess',
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
    'stable',
    'stable',
    'taxi_cool_service_stable'
),  (
    1,
    'pre_stable',
    'prestable',
    'taxi_cool_service_pre_stable'
), (
    1,
    'testing',
    'testing',
    'taxi_cool_service_testing'
), (
    1,
    'unstable_branch_name',
    'unstable',
    'taxi_cool_service_unstable'
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
    'service_info', 1, null,
    '{"deploy_callback_url": "http://frontend-dev-api.taxi.yandex.net/api/webhook/clownductor/deploy", "tvm_name": "remote-service"}'::jsonb,
    null::jsonb
);
