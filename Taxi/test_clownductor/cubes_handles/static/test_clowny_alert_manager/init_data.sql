INSERT INTO clownductor.namespaces (name) values ('taxi-infra');

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
    'taxi-infra',
    '_TAXIINFRATESTNETS_',
    '_TAXIINFRANETS_',
    'taxiinfraservicesdeploymanagement',
    'taxiinfraquotaypdefault',
    'taxiinfratvmaccess',
    '{"groups": ["vstimchenko"]}',
    '{}',
    '{}',
    'taxistoragepgaas',
    '{"stable": {"domain": "taxi-infra.yandex.net"}, "testing": {"domain": "taxi-infra.tst.yandex.net"}, "unstable": {"domain": "taxi-infra.dev.yandex.net"}}',
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
    'hejmdal',
    'artifact_name',
    'nanny',
    'DESIGN_REVIEW_TICKET-1',
    'https://wiki.yandex-team.ru/taxi/backend',
    'abc_service',
    'tvm_testing_abc_service',
    'tvm_stable_abc_service',
    'yc_postgres_project_id',
    'https://st.yandex-team.ru/NEW_TICKET-1',
    'alexrasyuk',
    'https://github.yandex-team.ru/taxi/backend-py3/blob/develop/clownductor/service.yaml'
),
(
    1,
    'alert-manager',
    'artifact_name',
    'nanny',
    'DESIGN_REVIEW_TICKET-1',
    'https://wiki.yandex-team.ru/taxi/backend',
    'abc_service',
    'tvm_testing_abc_service',
    'tvm_stable_abc_service',
    'yc_postgres_project_id',
    'https://st.yandex-team.ru/NEW_TICKET-1',
    'alexrasyuk',
    'https://github.yandex-team.ru/taxi/backend-py3/blob/develop/clownductor/service.yaml'
);

INSERT INTO clownductor.branches (
    service_id,
    name,
    env,
    direct_link,
    artifact_version,
    configs,
    deleted_at,
    balancer_id
) VALUES (
    1,
    'stable',
    'stable',
    'taxi_hejmdal_stable',
    '1.2.3',
    '["TEST_CONFIG"]',
    null,
    1
),
(
    2,
    'stable',
    'stable',
    'taxi_alert-manger_stable',
    '1.2.3',
    '["TEST_CONFIG"]',
    null,
    1
);


INSERT INTO clownductor.parameters (
    subsystem_name,
    service_id,
    branch_id,
    service_values,
    remote_values
) VALUES (
    'service_info',
    1,
    1,
    null,
    '{"duty_group_id": "taxidutyhejmdal"}'::jsonb
);
