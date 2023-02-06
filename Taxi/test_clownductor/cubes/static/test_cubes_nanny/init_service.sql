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
);

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
    'service_exist',
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
    'https://github.yandex-team.ru/taxi/backend-py3/blob/develop/clownductor/service.yaml'
),(
    1,
    'service_da',
    'postgrea_art_name',
    'postgres',
    'https://st.yandex-team.ru',
    'https://st.yandex-team.ru',
    'abc_service',
    'tvm_testing_abc_service',
    'tvm_stable_abc_service',
    'https://st.yandex-team.ru',
    'https://st.yandex-team.ru',
    'elrusso',
    'https://github.yandex-team.ru/taxi/backend-py3/blob/develop/clownductor/service2.yaml'
)
;

insert into clownductor.branches (
    service_id,
    name,
    env,
    direct_link
)
values
    (1, 'stable', 'stable', ''),
    (1, 'testing', 'testing', ''),
    (1, 'unstable', 'unstable' , ''),
    (1, 'pre_stable', 'prestable', ''),
    (2, 'stable', 'prestable', '')
;

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
    'in_progress'
)
;

insert into
    task_manager.job_variables (
    job_id,
    variables
)
values (
    1,
    '{"name": "DeployNannyServiceNoApprove", "image": "image_name", "comment": "test comment"}'
)
;
