INSERT INTO clownductor.namespaces (name) values ('taxi');

INSERT INTO clownductor.projects (
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
) VALUES (
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

INSERT INTO clownductor.services (
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
) VALUES (
    1,
    'service_nanny',
    'artifact_name',
    'nanny',
    'DESIGN_REVIEW_TICKET-1',
    'https://wiki.yandex-team.ru/taxi/backend',
    'abc_service',
    'tvm_testing_abc_service',
    'tvm_stable_abc_service',
    'yc_postgres_project_id',
    'https://st.yandex-team.ru/NEW_TICKET-1',
    'deoevgen',
    'https://github.yandex-team.ru/taxi/backend-py3/blob/develop/clownductor/service.yaml'
), (
    1,
    'service_mongo',
    'artifact_name',
    'mongo_mdb',
    'DESIGN_REVIEW_TICKET-1',
    'https://wiki.yandex-team.ru/taxi/backend',
    'abc_service',
    'tvm_testing_abc_service',
    'tvm_stable_abc_service',
    'yc_postgres_project_id',
    'https://st.yandex-team.ru/NEW_TICKET-1',
    'deoevgen',
    'https://github.yandex-team.ru/taxi/backend-py3/blob/develop/clownductor/service.yaml'
), (
    1,
    'service_postgres',
    'artifact_name',
    'postgres',
    'DESIGN_REVIEW_TICKET-1',
    'https://wiki.yandex-team.ru/taxi/backend',
    'abc_service',
    'tvm_testing_abc_service',
    'tvm_stable_abc_service',
    'yc_postgres_project_id',
    'https://st.yandex-team.ru/NEW_TICKET-1',
    'deoevgen',
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
)
values
    (1, 'stable', 'stable', 'taxi_cool_service_stable', '1.2.3', '[]', null, null),
    (2, 'stable', 'stable', 'mongo_cluster', '1.2.3', '[]', null, null),
    (3, 'stable', 'stable', 'postgres_cluster', '1.2.3', '[]', null, null)
;
