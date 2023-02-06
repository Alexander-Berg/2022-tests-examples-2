INSERT INTO clownductor.namespaces (name) values ('taxi'), ('eda'), ('cargo'), ('taxi-infra');

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
),
(
    'cargo',
    '_CARGOTESTNETS_',
    '_CARGONETS_',
    'cargoservicesdeploymanagement',
    'cargoquotaypdefault',
    'cargotvmaccess',
    '{"groups": ["d1mbas"]}',
    '{}',
    '{}',
    'taxistoragepgaas',
    '{"general": {"project_prefix": "taxi"}, "stable": {"domain": "cargo.yandex.net"}, "testing": {"domain": "cargo.tst.yandex.net"}, "unstable": {"domain": "cargo.dev.yandex.net"}}',
    '{"ops": [], "developers": [], "managers": [], "superusers": []}',
    '{"path": "taxi/taxi-access-log", "permissions": ["WriteTopic"]}',
    3
),
(
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
    '{"general": {"project_prefix": "taxi"}, "stable": {"domain": "taxi-infra.yandex.net"}, "testing": {"domain": "taxi-infra.tst.yandex.net"}, "unstable": {"domain": "taxi-infra.dev.yandex.net"}}',
    '{"ops": [], "developers": [], "managers": [], "superusers": []}',
    '{"path": "taxi/taxi-access-log", "permissions": ["WriteTopic"]}',
    4
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
    'https://a.yandex-team.ru/arc_vcs/taxi/uservices/services/partner-authproxy/service.yaml'
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
),
(
     1,
    '_elrusso_lxc_service',
    'artifact_name',
    'conductor',
    'https://st.yandex-team.ru',
    'https://st.yandex-team.ru',
    'abc_service',
    'tvm_testing_abc_service',
    'tvm_stable_abc_service',
    'srv4',
    'https://st.yandex-team.ru',
    'elrusso',
    null
),
(
    2,
    'srv5',
    'artifact_name',
    'nanny',
    'https://st.yandex-team.ru',
    'https://st.yandex-team.ru',
    'abc_service',
    'tvm_testing_abc_service',
    'tvm_stable_abc_service',
    'srv5',
    'https://st.yandex-team.ru',
    'deoevgen',
    null
),(
    3,
    'srv6',
    'artifact_name',
    'nanny',
    'https://st.yandex-team.ru',
    'https://st.yandex-team.ru',
    'abc_service_6',
    'tvm_testing_abc_service',
    'tvm_stable_abc_service',
    'srv6',
    'https://st.yandex-team.ru',
    'd1mbas',
    null
),(
    4,
    'srv7-no-branches-or-parameters',
    'artifact_name7',
    'nanny',
    'https://st.yandex-team.ru',
    'https://st.yandex-team.ru',
    'abc_service',
    'tvm_testing_abc_service7',
    'tvm_stable_abc_service7',
    'srv7',
    'https://st.yandex-team.ru',
    'vstimchenko',
    null
),(
    1,
    'srv8',
    'artifact_name',
    'nanny',
    'https://st.yandex-team.ru',
    'https://wiki.yandex-team.ru/taxi/backend',
    'abc_service',
    'tvm_testing_abc_service',
    'tvm_stable_abc_service',
    'srv8',
    'https://st.yandex-team.ru',
    'azhuchkov',
    'https://github.yandex-team.ru/taxi/backend-py3/blob/develop/clownductor/service.yaml'
),(
    1,
    'srv9',
    'artifact_name',
    'nanny',
    'https://st.yandex-team.ru',
    'https://wiki.yandex-team.ru/taxi/backend',
    'abc_service',
    'tvm_testing_abc_service',
    'tvm_stable_abc_service',
    'srv9',
    'https://st.yandex-team.ru',
    'azhuchkov',
    'https://github.yandex-team.ru/taxi/backend-py3/blob/develop/clownductor/service.yaml'
),(
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
    (1, 'stable', 'stable', 'taxi_cool_service_stable', '1.2.3', '["TEST_CONFIG", "BURGER"]', null, 1),
    (1, 'testing', 'testing', 'taxi_cool_service_testing', null , '[]', null, null),
    (2, 'stable', 'stable', 'taxi_cool_service_stable', null , '[]', null, null),
    (2, 'pre_stable', 'prestable', 'taxi_nanny_service_pre_stable', null , '[]', null, null),
    (3, 'stable', 'stable', 'eda_nanny_srv3_stable', null , '[]', null, null),
    (3, 'pre_stable', 'prestable', 'eda_nanny_srv3_pre_stable', null , '[]', null, null),
    (5, 'stable_br_7', 'stable', 'eda_nanny_srv5_stable', null , '[]', null, null),
    (5, 'pre_stable_br_8', 'prestable', 'eda_nanny_srv5_pre_stable', null , '[]', null, null),
    (6, 'stable', 'stable', 'taxi_nanny_srv6_stable', null , '[]', null, null),
    (6, 'pre_stable', 'prestable', 'taxi_nanny_srv6_pre_stable', null , '[]', null, null),
    (8, 'stable', 'stable', 'taxi_nanny_srv8_stable', null , '[]', null, null),
    (9, 'stable', 'stable', 'taxi_nanny_srv9_stable', null , '[]', null, null),
    (10, 'stable', 'stable', 'taxi_nanny_srv10_stable', null , '[]', null, null),
    (4, 'stable', 'stable', 'taxi_srv4', null , '[]', null, null)
    ;

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
        '{"critical_class": "A", "service_yaml_url": "https://github.yandex-team.ru/taxi/backend-py3/blob/develop/clownductor/elrusso_service.yaml" ,"wiki_path": "https://wiki.yandex-team.ru/taxi/elrusso_service", "clownductor_project": "test", "service_type": "backendpy3", "duty_group_id": "42", "description": "Like conductor but with a twist.", "yt_log_replications": [{"table":"some_table", "url": "https://yt.yandex-team.ru/arnold/"}]}'::jsonb,
        '{"wiki_path": "https://wiki.yandex-team.ru/taxi/elrusso_service", "clownductor_project": "test", "service_type": "backendpy3", "duty_group_id": "42"}'::jsonb
    ),
    (
        'service_info', 1, 1,
        '{"robots": ["robot-tester", "nanny-robot"], "network": "__MY_NETWORK__", "duty_group_id": "yaml_group_id"}'::jsonb,
        '{"robots": ["robot-tester", "nanny-robot"], "network": "__MY_NETWORK__", "duty_group_id": "remote_group_id", "duty": {"abc_slug": "common_abc_slug", "primary_schedule": "primary_shedule_service"}}'::jsonb
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
        '{"clownductor_project": "test", "service_type": "backendpy3", "duty_group_id": "42"}'::jsonb
    ),
    (
        'service_info', 2, 2,
        '{"grafana": "https://grafana.yandex-team.ru/d/KP2m9Ol2w/nanny_service_2_testing"}'::jsonb,
        null
    ),
    (
        'service_info', 2, 3,
        '{"grafana": "https://grafana.yandex-team.ru/d/VmI0OSsWk/nanny_service_2_stable"}'::jsonb,
        '{"robots": ["robot-tester", "nanny-robot"], "network": "__MY_NETWORK__", "duty_group_id": "remotegroup42"}'::jsonb
    ),
    (
        'service_info', 3, null,
        '{"responsible_managers": ["d1mbas"]}'::jsonb,
        '{"responsible_managers": ["d1mbas"]}'::jsonb
    ),
    (
        'abc', 4, null,
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
        'service_info', 5, 7,
        '{"grafana": "TODO"}'::jsonb,
        null
    ),(
        'abc', 9, 12,
        '{
        "maintainers": ["azhuchkov", "meow"],
        "service_name": {"ru": "Сервис", "en": "Service"},
        "description": {"ru": "Сервис", "en": "Service"}
        }'::jsonb,
        null
    ),(
        'abc', 10, 13,
        '{
        "maintainers": ["azhuchkov", "meow"],
        "service_name": {"ru": "Сервис", "en": "Service"},
        "description": {"ru": "Сервис", "en": "Service"}
        }'::jsonb,
        null
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
    ('deploy_approve_manager', 'd1mbas', NULL, 2),
    ('deploy_approve_programmer', 'deoevgen', NULL, 3),
    ('deploy_approve_programmer', 'deoevgen', 6, NULL)
;

insert into clownductor.service_issues (service_id, issue_key, issue_parameters)
values (
    10,
    'maintainer_dismiss',
    '{"dismissed_maintainers": "meow"}'::jsonb
),
(
    10,
    'service_yaml_missed',
    '{}'::jsonb
),
(
    10,
    'service_yaml_is_broken',
    '{}'::jsonb
),
(
    10,
    'duty_group_missed',
    '{}'::jsonb
),
(
    5,
    'duty_group_is_empty',
    '{}'::jsonb
),
(
    2,
    'maintainer_absence',
    '{}'::jsonb
),
(
    3,
    'service_yaml_missed',
    '{}'::jsonb
)
;
