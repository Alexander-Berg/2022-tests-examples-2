insert into clownductor.namespaces (name) values ('taxi'), ('eda');

insert into clownductor.projects (
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
), (
    'test_eda_project',
    '_EDATESTNETS_',
    '_HWEDANETS_',
    'edaservicesdeploymanagement',
    'edaquotaypdefault',
    'edatvmaccess',
    2
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
    'nanny',
    'unit_test',
    'abc_service',
    'https://github.yandex-team.ru/taxi/uservices/blob/develop/services/test_service/service.yaml'
), (
    1,
    'test_service_2',
    'taxi/test_service_2/$',
    'nanny',
    'unit_test',
    'abc_service',
    'https://github.yandex-team.ru/taxi/uservices/blob/develop/services/test_service/service.yaml'
), (
    1,
    'test_service_3',
    'taxi/test_service_3/$',
    'nanny',
    'unit_test',
    'abc_service',
    'https://github.yandex-team.ru/taxi/uservices/blob/develop/services/test_service/service.yaml'
), (
    1,
    'test_service_4',
    'taxi/test_service_4/$',
    'nanny',
    'unit_test',
    'abc_service',
    null
), (
    2,
    'test_service_4',
    'taxi/test_service_4/$',
    'nanny',
    'unit_test',
    'abc_service',
    null
), (
    1,
    'test_service_5',
    'taxi/test_service_5/$',
    'nanny',
    'unit_test',
    'abc_service',
    null
), (
    2,
    'test_service_5',
    'taxi/test_service_5/$',
    'nanny',
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
    'unstable',
    'unstable',
    'test_service_unstable'
), (
    1,
    'stable',
    'stable',
    'test_service_stable'
), (
    2,
    'unstable',
    'unstable',
    'test_service_2_unstable'
), (
    2,
    'stable',
    'stable',
    'test_service_2_stable'
), (
    3,
    'unstable',
    'unstable',
    'test_service_3_unstable'
), (
    3,
    'stable',
    'stable',
    'test_service_3_stable'
), (
    1,
    'prestable',
    'prestable',
    'test_service_pre_stable'
), (
    2,
    'prestable',
    'prestable',
    'test_service_2_pre_stable'
), (
    3,
    'prestable',
    'prestable',
    'test_service_3_pre_stable'
), (
    4,
    'stable',
    'stable',
    'test_project_service_4_stable'
), (
    4,
    'prestable',
    'prestable',
    'test_project_service_pre_4_stable'
), (
    5,
    'stable',
    'stable',
    'test_eda_project_service_4_stable'
), (
    5,
    'prestable',
    'prestable',
    'test_eda_project_service_pre_4_stable'
), (
    6,
    'stable',
    'stable',
    'test_project_service_5_stable'
), (
    6,
    'prestable',
    'prestable',
    'test_project_service_pre_5_stable'
), (
    7,
    'stable',
    'stable',
    'test_eda_project_service_5_stable'
), (
    7,
    'prestable',
    'prestable',
    'test_eda_project_service_pre_5_stable'
)
;
