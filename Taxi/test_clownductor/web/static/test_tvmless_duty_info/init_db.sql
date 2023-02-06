INSERT INTO clownductor.namespaces (name) values ('taxi'), ('eda');

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
),
(
    'eda',
    '_EDATESTNETS_',
    '_EDANETS_',
    'edaservicesdeploymanagement',
    'edaquotaypdefault',
    'edatvmaccess',
    '{"groups": ["d1mbas"]}',
    '{}',
    '{}',
    'taxistoragepgaas',
    '{"stable": {"domain": "eda.yandex.net"}, "testing": {"domain": "eda.tst.yandex.net"}, "unstable": {"domain": "eda.dev.yandex.net"}}',
    '{"ops": [], "developers": [], "managers": [], "superusers": []}',
    '{"path": "taxi/taxi-access-log", "permissions": ["WriteTopic"]}',
    2
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
    'service_exist',
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
), (
    1,
    'service_2',
    'artifact_name',
    'nanny',
    '',
    '',
    'abc_service',
    'tvm_testing_abc_service',
    'tvm_stable_abc_service',
    'service_2',
    '',
    'deoevgen',
    null
),
(
    2,
    'srv3',
    'artifact_name',
    'nanny',
    'https://st.yandex-team.ru',
    'https://st.yandex-team.ru',
    'abc_service',
    'tvm_testing_abc_service',
    'tvm_stable_abc_service',
    'srv3',
    'https://st.yandex-team.ru',
    'd1mbas',
    null
);

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
    (1, 'stable', 'stable', 'test_nanny_service', '1.2.3', '["TEST_CONFIG", "BURGER"]', null, 1),
    (2, 'testing', 'testing', 'test_nanny_service', null , '[]', null, null),
    (2, 'stable', 'stable', 'test_nanny_service_stable', null , '[]', null, null),
    (2, 'pre_stable', 'prestable', 'test_nanny_service_pre_stable', null , '[]', null, null),
    (3, 'stable', 'stable', 'test_nanny_srv3_stable', null , '[]', null, null);

insert into clownductor.parameters (
    subsystem_name,
    service_id,
    branch_id,
    service_values,
    remote_values
)
values
    (
        'service_info', 1, null,
        '{"clownductor_project": "test", "service_type": "backendpy3", "duty_group_id": "42", "description": "Like conductor but with a twist.", "yt_log_replications": [{"table":"some_table", "url": "https://yt.yandex-team.ru/arnold/"}]}'::jsonb,
        '{"clownductor_project": "test", "service_type": "backendpy3", "duty_group_id": "42"}'::jsonb
    ),
    (
        'service_info', 1, 1,
        '{"grafana": "https://grafana.yandex-team.ru/d/LVu3OitWk/nanny_taxi_clownductor_stable", "robots": ["robot-tester", "nanny-robot"], "network": "__MY_NETWORK__", "duty_group_id": "elrusso_band"}'::jsonb,
        '{"grafana": "https://grafana.yandex-team.ru/d/LVu3OitWk/nanny_taxi_clownductor_stable", "robots": ["robot-tester", "nanny-robot"], "network": "__MY_NETWORK__", "duty_group_id": "elrusso_band", "duty": {"abc_slug": "common_abc_slug", "primary_schedule": "primary_shedule_service"}}'::jsonb
    ),
    (
        'nanny', 1, 1,
        '{"cpu": 1000, "ram": 1000, "root_size": 10240, "work_dir": 512, "instances": 1, "datacenters_count": 2, "persistent_volumes": [{"size": 10240, "path": "/logs", "type": "hdd"}]}'::jsonb,
        '{"cpu": 1000, "ram": 1000, "root_size": 5120, "work_dir": 256, "instances": 1, "datacenters_count": 2}'::jsonb
    ),
    (
        'nanny', 1, 2,
        '{"cpu": 1000, "ram": 1000, "root_size": 10240, "work_dir": 512, "instances": 2, "datacenters_count": 2}'::jsonb,
        '{"cpu": 1000, "ram": 1000, "root_size": 10240, "work_dir": 512, "instances": 1, "datacenters_count": 1}'::jsonb
    ),
    (
        'abc', 1, 1,
        '{
        "maintainers": ["karachevda", "meow"],
        "service_name": {"ru": "Сервис", "en": "Service"},
        "description": {"ru": "Сервис", "en": "Service"}
        }'::jsonb,
        '{
        "maintainers": ["kus", "karachevda"],
        "service_name": {"ru": "Крутой Сервис", "en": "Cool Service"},
        "description": {"ru": "Сервис", "en": "Service"}
        }'::jsonb
    ),
        (
        'service_info', 2, null,
        '{"yt_log_replications": null}'::jsonb,
        '{"clownductor_project": "test", "service_type": "backendpy3", "duty_group_id": "elrusso_band"}'::jsonb
    ),
       (
        'service_info', 3, null,
        '{"clownductor_project": "test", "service_type": "backendpy3", "duty_group_id": null}'::jsonb,
        '{"clownductor_project": "test", "service_type": "backendpy3", "duty_group_id": null}'::jsonb
    );

insert into task_manager.jobs (
	    service_id,
	    branch_id,
	    name,
	    initiator,
	    status,
	    created_at,
	    finished_at
	    )
values (
    1,
    1,
    'DeployNannyServiceWithApprove',
    'deoevgen',
    'canceled',
    1602571407,
    1602574131
),
(
    2,
    2,
    'WaitMainDeployNannyServiceWithApprove',
    'deoevgen',
    'canceled',
    1602571408,
    1602574132
),
(
    2,
    2,
    'DeployNannyServiceWithApprove',
    'deoevgen',
    'canceled',
    1602571409,
    1602574133
),
(
    1,
    1,
    'ResolveServiceDiff',
    'deoevgen',
    'canceled',
    1602571409,
    1602574133
)
;

insert into task_manager.job_variables (
    job_id,
    variables
)
values (
    1,
    '{}'
),
(
    2,
    '{"job_id": 2}'
),
(
    3,
    '{}'
),
(
    4,
    '{}'
)
;

INSERT INTO permissions.roles (role, login, service_id, project_id)
VALUES
    ('deploy_approve_programmer', 'd1mbas', 1, NULL),
    ('deploy_approve_programmer', 'deoevgen', 1, NULL),
    ('deploy_approve_programmer', 'd1mbas', 2, NULL),
    ('deploy_approve_manager', 'd1mbas', NULL, 2)
;
