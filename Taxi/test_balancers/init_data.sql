insert into clownductor.namespaces (name) values ('taxi');

insert into clownductor.projects (
    name,
    network_testing,
    network_stable,
    service_abc,
    yp_quota_abc,
    tvm_root_abc,
    owners,
    env_params,
    namespace_id
)
values (
    'test_project',
    '_TAXITESTNETS_',
    '_HWTAXINETS_',
    'taxiservicesdeploymanagement',
    'taxiquotaypdefault',
    'taxitvmaccess',
    '{"groups": [], "logins": []}'::jsonb,
    '{"stable": {"domain": "taxi.yandex.net"}, "testing": {"domain": "taxi.tst.yandex.net"}, "unstable": {"domain": "taxi.dev.yandex.net"}}'::jsonb,
    1
)
;

insert into clownductor.services (
    project_id,
    name,
    artifact_name,
    cluster_type,
    requester,
    abc_service
)
values (
    1,
    'test_service',
    'taxi/test_service/$',
    'nanny',
    'unit_test',
    'abc_service'
)
;

insert into clownductor.branches (
    service_id,
    name,
    env,
    direct_link
)
values (
    1,
    'testing',
    'testing',
    'test_service_testing'
), (
    1,
    'tcustom',
    'testing',
    'test_service_tcustom'
), (
    1,
    'pre_stable',
    'prestable',
    'test_service_prestable'
), (
    1,
    'stable',
    'stable',
    'test_service_stable'
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
    'success'
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
    4,
    '{"network": "__ELRUSSO_STABLE"}'::jsonb,
    '{"network": "__ELRUSSO_STABLE"}'::jsonb
)
;
