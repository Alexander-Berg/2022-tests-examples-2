insert into clownductor.namespaces (name) values ('taxi');

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
    '{"cgroups": [123, 234]}',
    '{"cgroups": [123, 234]}',
    'taxistoragepgaas',
    '{"stable": {"domain": "taxi.yandex.net"}, "testing": {"domain": "taxi.tst.yandex.net"}, "unstable": {"domain": "taxi.dev.yandex.net"}}',
    '{"ops": [], "developers": [], "managers": [], "superusers": []}',
    '{"path": "taxi/taxi-access-log", "permissions": ["WriteTopic"]}',
    1
);

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
    'test_service',
    'artifact_name',
    'nanny',
    'https://st.yandex-team.ru',
    'https://st.yandex-team.ru',
    'abc_service',
    'tvm_testing_abc_service',
    'tvm_stable_abc_service',
    'https://st.yandex-team.ru',
    'https://st.yandex-team.ru',
    'deoevgen',
    'https://github.yandex-team.ru/taxi/backend-py3/blob/develop/services/clownductor/service.yaml'
),(
    1,
    'non_service_yaml',
    'artifact_name',
    'nanny',
    'https://st.yandex-team.ru',
    'https://st.yandex-team.ru',
    'abc_service',
    'tvm_testing_abc_service',
    'tvm_stable_abc_service',
    'https://st.yandex-team.ru',
    'https://st.yandex-team.ru',
    'deoevgen',
    null
),
(
    1,
    'test_service_in_arcadia',
    'artifact_name',
    'nanny',
    'https://st.yandex-team.ru',
    'https://st.yandex-team.ru',
    'abc_service',
    'tvm_testing_abc_service',
    'tvm_stable_abc_service',
    'https://st.yandex-team.ru',
    'https://st.yandex-team.ru',
    'spolischouck',
    'https://a.yandex-team.ru/arc_vcs/taxi/backend-py3/services/clownductor/service.yaml'
)
;
