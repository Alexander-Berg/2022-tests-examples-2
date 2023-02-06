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
    'https://github.yandex-team.ru/taxi/backend-py3/blob/develop/test_cubes_internal/service.yaml'
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
    'single_service',
    'artifact_name_single',
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
)
;

insert into clownductor.branches (
    service_id,
    name,
    env,
    direct_link
)
values
    (1, 'stable', 'stable', 'stable_nanny_name'),
    (1, 'pre_stable', 'prestable', 'prestable_nanny_name'),
    (1, 'testing', 'testing', 'testing_nanny_name'),
    (2, 'stable', 'stable', 'stable_nanny_name_short'),
    (2, 'pre_stable', 'prestable', 'prestable_nanny_name_short'),
    (3, 'stable', 'stable', 'stable_nanny_name_single'),
    (3, 'pre_stable', 'prestable', 'prestable_nanny_name_single')
;

INSERT INTO task_manager.locks (name, job_id)
VALUES ('Deploy.taxi_test_service_stable', 1)
;

INSERT INTO task_manager.jobs (
	        service_id,
	        branch_id,
	        name,
	        initiator,
	        idempotency_token,
	        tp_change_doc_id,
	        remote_job_id,
	        status
	    )
VALUES (
    1,
    null,
    'WaitMainDeployNannyServiceNoApprove',
    'elrusso',
    'idemp-WaitMainDeployNannyServiceNoApprove-sandbox-service_id=354834-branch_id=295196-b63dc425a1f14a428c1e2a96b537440f',
    'WaitMainDeployNannyServiceNoApprove-354834-295196-deploy_type=sandbox',
    null,
    'in_progress'
),
(
    1,
    null,
    'WaitMainDeployNannyServiceNoApprove',
    'elrusso',
    'idemp-WaitMainDeployNannyServiceNoApprove-sandbox-service_id=354389-branch_id=294775-d79ff707ccfe47e896c31a509910b73d',
    'WaitMainDeployNannyServiceNoApprove-354389-294775-deploy_type=sandbox',
    null,
    'in_progress'
),
(
    2,
    null,
    'WaitMainDeployNannyServiceNoApprove',
    'elrusso',
    'idemp-WaitMainDeployNannyServiceNoApprove-sandbox-service_id=40000-branch_id=294775-d79ff707ccfe47e896c31a509910b73d',
    'WaitMainDeployNannyServiceNoApprove-40000-294775-deploy_type=sandbox',
    null,
    'in_progress'
)
;


INSERT INTO task_manager.job_variables (
    job_id,
    variables
)
VALUES (
    1,
    '{"release_ticket_st": "TAXIREL-33245"}'
),
(
    2,
    '{"job_id": 1, "wait_delay": 10}'
),
(
    3,
    '{"release_ticket_st": "TAXIREL-40000"}'
)
;
