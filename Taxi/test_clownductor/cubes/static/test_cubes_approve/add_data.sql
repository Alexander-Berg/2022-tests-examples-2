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
    'service_exist',
    'artifact_name',
    'nanny',
    'https://st.yandex-team.ru',
    'https://st.yandex-team.ru',
    'abc_service_exist',
    'tvm_testing_abc_service',
    'tvm_stable_abc_service',
    'taxi_service_exist',
    'https://st.yandex-team.ru',
    'deoevgen',
    'https://github.yandex-team.ru/taxi'
),
(
    1,
    'second_service_exist',
    'artifact_name',
    'nanny',
    'https://st.yandex-team.ru',
    'https://st.yandex-team.ru',
    'abc_second_service_exist',
    'tvm_testing_abc_service',
    'tvm_stable_abc_service',
    'https://st.yandex-team.ru',
    'https://st.yandex-team.ru',
    'd1mbas',
    'https://github.yandex-team.ru/taxi'
),
(
    1,
    'one_more_service',
    'artifact_name',
    'nanny',
    'https://st.yandex-team.ru',
    'https://st.yandex-team.ru',
    'abc_one_more_service',
    'tvm_testing_abc_service',
    'tvm_stable_abc_service',
    'https://st.yandex-team.ru',
    'https://st.yandex-team.ru',
    'd1mbas',
    'https://github.yandex-team.ru/taxi'
);

INSERT INTO permissions.roles (role, login, service_id, project_id, is_super)
VALUES ('deploy_approve_programmer', 'd1mbas', 1, NULL, FALSE),
       ('deploy_approve_programmer', 'isharov', NULL, 1, FALSE),
       ('deploy_approve_programmer', 'oxcd8o', NULL, 1, FALSE),
       ('deploy_approve_programmer', 'nevladov', NULL, NULL, TRUE),
       ('deploy_approve_manager', 'effeman', 1 , NULL, FALSE)
;

INSERT INTO clownductor.branches (
    service_id,
    name,
    env,
    direct_link
)
VALUES (
    1,
    'pre_stable',
    'prestable',
    'taxi_service_exist_pre_stable'
);

INSERT INTO task_manager.jobs
    (service_id, branch_id, status, remote_job_id)
VALUES (1, 1, 'inited', 1);

insert into clownductor.parameters (
    subsystem_name,
    service_id,
    branch_id,
    service_values,
    remote_values
) values (
    'service_info', 2, null,
    '{"responsible_managers": ["regular-manager"]}'::jsonb,
    '{"responsible_managers": ["regular-manager"]}'::jsonb
);
