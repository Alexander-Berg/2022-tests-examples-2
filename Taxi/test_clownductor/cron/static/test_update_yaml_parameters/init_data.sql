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
        abc_service,
        service_url
    )
values (
    1,
    'test-service',
    'artifact_name',
    'nanny',
    'unit_test',
    'abc_service',
    'https://github.yandex-team.ru/taxi/backend-py3/blob/develop/service-1/service.yaml'
), (
    1,
    'test-service-2',
    'artifact_name_2',
    'nanny',
    'unit_test',
    'abc_service_2',
    'https://github.yandex-team.ru/taxi/backend-py3/blob/develop/service-2/service.yaml'
), (
    1,
    'test-service-3',
    'artifact_name_3',
    'conductor',
    'unit_test',
    'abc_service_3',
    'https://github.yandex-team.ru/taxi/backend-py3/blob/develop/service-3/service.yaml'
), (
    1,
    'test-service-4',
    'artifact_name_4',
    'nanny',
    'unit_test',
    'abc_service_4',
    null
),
(
    1,
    'elrusso4-service',
    'artifact_name-5',
    'conductor',
    'unit_test',
    'abc_service_5',
    'https://github.yandex-team.ru/taxi/backend-py3/blob/develop/service-4/service.yaml'
),
(
    1,
    'elrusso4_bad_yaml-service',
    'artifact_name-5',
    'nanny',
    'unit_test',
    'abc_service_5',
    'https://github.yandex-team.ru/taxi/backend-py3/blob/develop/service-5/service.yaml'
),
(
    1,
    'elrusso4_no_yaml-service',
    'artifact_name-5',
    'nanny',
    'unit_test',
    'abc_service_5',
    'https://github.yandex-team.ru/taxi/backend-py3/blob/develop/service-not_found/service.yaml'
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
), (
    2,
    'stable_branch',
    'stable',
    'test-service-2-direct'
), (
    1,
    'pre_stable_branch',
    'prestable',
    'test-service-pre-1-direct'
),
(
    3,
    'stable_branch',
    'stable',
    'test-service-3-direct'
)
;

insert into clownductor.service_issues (
    service_id,
    issue_key,
    issue_parameters
) values (
    1,
    'service_yaml_is_broken',
    '{}'::jsonb
),
(
    6,
    'service_yaml_missed',
    '{}'::jsonb
)
;
