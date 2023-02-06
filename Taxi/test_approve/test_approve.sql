insert into clownductor.namespaces (name) values ('taxi');

INSERT INTO clownductor.projects (
    name,
    network_testing,
    network_stable,
    service_abc,
    yp_quota_abc,
    tvm_root_abc,
    namespace_id
)
VALUES (
    'test_project',
    '_TAXITESTNETS_',
    '_HWTAXINETS_',
    'taxiservicesdeploymanagement',
    'taxiquotaypdefault',
    'taxitvmaccess',
    1
)
;

insert into clownductor.services (
    project_id,
    name,
    artifact_name,
    cluster_type,
    requester,
    abc_service,
    direct_link
)
values (
    1,
    'test_service',
    'taxi/test_service/$',
    'nanny',
    'unit_test',
    'abc_service',
    'taxi_test_service'
), (
    1,
    'test-service',
    'taxi/test-service/$',
    'nanny',
    'unit_test',
    'abc_service',
    'taxi_test_service'
), (
    1,
    'cool_service',
    'taxi/cool_service/$',
    'nanny',
    'unit_test',
    'abc_service',
    'taxi_cool_service'
)
;

insert into clownductor.branches (
    id,
    service_id,
    name,
    env,
    direct_link
)
values (
    1,
    1,
    'unstable_branch',
    'unstable',
    'test_service_unstable'
), (
    2,
    2,
    'stable_branch',
    'stable',
    'taxi_test-service_stable'
), (
    3,
    3,
    'stable',
    'stable',
    'taxi_cool_service_stable'
), (
    4,
    3,
    'pre_stable',
    'prestable',
    'taxi_cool_service_pre_stable'
), (
    5,
    3,
    'testing',
    'testing',
    'taxi_cool_service_testing'
);

insert into task_manager.jobs (
    id,
    service_id,
    branch_id,
    name,
    initiator,
    status
)
values (
    1,
    1,
    1,
    'DeployNannyServiceNoApprove',
    'deoevgen',
    'canceled'
),
(
    456,
    1,
    1,
    'DeployNannyServiceNoApprove',
    'd1mbas',
    'in_progress'
)
;

insert into clownductor.parameters (
    subsystem_name,
    service_id,
    branch_id,
    service_values,
    remote_values
) values (
    'service_info', 1, null,
    '{"responsible_managers": ["0"], "release_flow": {"separate_sandbox_developers": true}}'::jsonb,
    '{"responsible_managers": ["0"]}'::jsonb
), (
    'service_info', 2, 2,
    '{"grafana": "https://grafana.yandex-team.ru/dashboard/db/taxi_test-service_stable_grafana_link_from_database"}'::jsonb,
    null
);
