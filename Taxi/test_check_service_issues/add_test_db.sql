insert into clownductor.namespaces (name) values ('taxi');

insert into clownductor.projects (
    name,
    network_testing,
    network_stable,
    service_abc,
    yp_quota_abc,
    tvm_root_abc,
    owners,
    approving_managers,
    approving_devs,
    pgaas_root_abc,
    env_params,
    responsible_team,
    yt_topic,
    namespace_id
) values (
    'taxi',
    '_TAXITESTNETS_',
    '_HWTAXINETS_',
    'taxiservicesdeploymanagement',
    'taxiquotaypdefault',
    'taxitvmaccess',
    '{"groups": ["deoevgen"]}',
    '{}',
    '{}',
    'taxistoragepgaas',
    '{"stable": {"domain": "taxi.yandex.net"}, "testing": {"domain": "taxi.tst.yandex.net"}, "unstable": {"domain": "taxi.dev.yandex.net"}}',
    '{"ops": [], "developers": [], "managers": [], "superusers": []}',
    '{"path": "taxi/taxi-access-log", "permissions": ["WriteTopic"]}',
    1
)
;

insert into clownductor.services (
    project_id,
    name,
    artifact_name,
    cluster_type,
    design_review_ticket,
    wiki_path,
    abc_service,
    tvm_testing_abc_service,
    tvm_stable_abc_service,
    direct_link,
    new_service_ticket,
    requester,
    service_url
) values (
    1,
    'srv10',
    'artifact_name',
    'nanny',
    'https://st.yandex-team.ru',
    'https://wiki.yandex-team.ru/taxi/backend',
    'abc_service',
    'tvm_testing_abc_service',
    'tvm_stable_abc_service',
    'srv10',
    'https://st.yandex-team.ru',
    'azhuchkov',
    'https://github.yandex-team.ru/taxi/backend-py3/blob/develop/clownductor/service.yaml'
),
(
    1,
    'post_10',
    'artifact_name_db',
    'postgres',
    'https://st.yandex-team.ru',
    'https://wiki.yandex-team.ru/taxi/backend',
    'abc_service_db',
    'tvm_testing_abc_service',
    'tvm_stable_abc_service',
    'srv10',
    'https://st.yandex-team.ru',
    'elrusso',
    'https://github.yandex-team.ru/taxi/backend-py3/blob/develop/clownductor/service.yaml'
)
;

insert into clownductor.branches (
    service_id,
    name,
    env,
    direct_link,
    artifact_version,
    configs,
    deleted_at,
    balancer_id
) values (
    1,
    'stable',
    'stable',
    'test_nanny_srv10_stable',
    null ,
    '[]',
    null,
    null
),
(
    2,
    'stable',
    'stable',
    'test_nanny_srv10_stable',
    null ,
    '[]',
    null,
    null
)
;

insert into clownductor.parameters (
    subsystem_name,
    service_id,
    branch_id,
    service_values,
    remote_values
) values (
    'abc',
    1,
    1,
    '{
    "maintainers": ["azhuchkov", "meow"],
    "service_name": {"ru": "Сервис", "en": "Service"},
    "description": {"ru": "Сервис", "en": "Service"}
    }'::jsonb,
    null
),
(
    'service_info',
    1,
    1,
    '{
    "clownductor_project": "test_project"
    }'::jsonb,
    '{
    }'::jsonb
)
;
