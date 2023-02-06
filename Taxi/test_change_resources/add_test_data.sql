insert into clownductor.namespaces (name) values ('taxi');

insert into clownductor.projects (
    name,
    network_testing,
    network_stable,
    service_abc,
    yp_quota_abc,
    tvm_root_abc,
    responsible_team,
    namespace_id
)
values (
    'test_project',
    '_TAXITESTNETS_',
    '_HWTAXINETS_',
    'taxiservicesdeploymanagement',
    'taxiquotaypdefault',
    'taxitvmaccess',
    '{"ops": ["yandex_rkub_taxi_5151_8501_9282_dep50822"], "managers": [], "developers": [], "superusers": ["isharov", "nikslim"]}',
    1
), (
    'taxi',
    '_TAXITESTINFRA_',
    '_HWTAXINETS_',
    'taxiservicesdeploymanagement',
    'taxiquotaypdefault',
    'taxitvmaccess',
    '{"ops": ["yandex_rkub_taxi_5151_8501_9282_dep50822"], "managers": [], "developers": [], "superusers": ["isharov", "nikslim"]}',
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
    direct_link,
    service_url
)
values (
    1,
    'test_service',
    'taxi/test_service/$',
    'postgres',
    'unit_test',
    'abc_service',
    null,
    null
), (
    2,
    'some_service',
    'taxi/some_service/$',
    'nanny',
    'unit_test',
    'abc_service',
    'test_direct',
    null
), (
    1,
    'test_yaml_generate',
    'taxi/test_yaml_generate/$',
    'nanny',
    'unit_test',
    'abc_service',
    null,
    'https://github.yandex-team.ru/taxi/uservices/blob/develop/services/route-calc/service.yaml'
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
    'unstable_branch_1',
    'unstable',
    'test_service_unstable'
), (
    2,
    'unstable_branch_2',
    'unstable',
    'path'
), (
    3,
    'prestable_branch_3',
    'prestable',
    'path'
), (
    3,
    'prestable_branch_4',
    'stable',
    'path_test'
), (
    3,
    'unstable_branch_5',
    'unstable',
    'test_service_unstable'
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
), (
    1,
    1,
    'ResolveServiceDiff',
    'deoevgen',
    'success'
), (
    2,
    2,
    'ResolveServiceDiff',
    'deoevgen',
    'success'
)
;
