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
    service_url
)
values (
    1,
    'test_service',
    'taxi/test_service/$',
    'postgres',
    'unit_test',
    'abc_service',
    'https://github.yandex-team.ru/taxi/uservices/blob/develop/services/test_service/service.yaml'
), (
    1,
    'test_service_db',
    'taxi/test_service/$',
    'postgres',
    'unit_test',
    'abc_service',
    null
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
    'stable',
    'stable',
    'test_service_stable'
), (
    2,
    'testing',
    'testing',
    'testing_cluster_id'
), (
    2,
    'stable',
    'stable',
    'stable_cluster_id'
)
;
