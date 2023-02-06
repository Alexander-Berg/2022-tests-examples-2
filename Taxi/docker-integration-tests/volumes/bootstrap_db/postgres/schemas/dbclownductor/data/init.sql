INSERT INTO clownductor.namespaces (name)
VALUES ('taxi');

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
'{"groups": ["common_instruments"], "logins": ["elrusso"]}',
'{}',
'{}',
'taxistoragepgaas',
'{"stable": {"domain": "taxi.yandex.net"}, "testing": {"domain": "taxi.tst.yandex.net"}, "unstable": {"domain": "taxi.dev.yandex.net"}}',
'{"ops": [], "developers": [], "managers": [], "superusers": []}',
'{"path": "taxi/taxi-access-log", "permissions": ["WriteTopic"]}',
1
),
(
'taxi_integration_test_project',
'_TAXITESTNETS_',
'_HWTAXINETS_',
'taxiservicesdeploymanagement',
'taxiquotaypdefault',
'taxitvmaccess',
'{"groups": ["common_instruments"], "logins": ["elrusso"]}',
'{}',
'{}',
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
    st_task,
    design_review_ticket,
    wiki_path,
    repo_path,
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
'https://st.yandex-team.ru',
'https://st.yandex-team.ru',
'abc_service',
'tvm_testing_abc_service',
'tvm_stable_abc_service',
'https://st.yandex-team.ru',
'https://st.yandex-team.ru',
'deoevgen',
'https://github.yandex-team.ru/taxi/backend-py3/blob/develop/clownductor/service.yaml'
), (
1,
'service_2',
'artifact_name',
'nanny',
'https://st.yandex-team.ru',
'https://st.yandex-team.ru',
'https://st.yandex-team.ru',
'https://st.yandex-team.ru',
'abc_service',
'tvm_testing_abc_service',
'tvm_stable_abc_service',
'https://st.yandex-team.ru',
'https://st.yandex-team.ru',
'deoevgen',
null
),(
1,
'admin-users-info',
'artifact_name',
'conductor',
'https://st.yandex-team.ru',
'https://st.yandex-team.ru',
'https://wiki.yandex-team.ru',
'https://st.yandex-team.ru',
'abc_service',
'tvm_testing_abc_service',
'tvm_stable_abc_service',
'https://st.yandex-team.ru',
'https://st.yandex-team.ru',
'elrusso',
'https://github.yandex-team.ru/taxi/backend-py3/blob/develop/admin-users-info/service.yaml'
),
(
2,
'envoy-exp-bravo',
'artifact_name',
'nanny',
'TAXIADMIN-9711',
'https://st.yandex-team.ru',
'https://wiki.yandex-team.ru',
'https://st.yandex-team.ru',
'abc_service',
'envoy-exp-bravo',
'envoy-exp-bravo',
'taxi_tst_envoy-exp-bravo-NOT-THE-DIRECT-LINK-USEFUL-FOR-SCOUT',
'https://st.yandex-team.ru',
'elrusso',
'https://github.yandex-team.ru/taxi/backend-py3/blob/develop/admin-users-info/service.yaml'
),
(
2,
'envoy-exp-charlie',
'artifact_name',
'nanny',
'TAXIADMIN-9711',
'https://st.yandex-team.ru',
'https://wiki.yandex-team.ru',
'https://st.yandex-team.ru',
'abc_service',
'envoy-exp-charlie',
'envoy-exp-charlie',
'taxi_tst_envoy-exp-charlie-NOT-THE-DIRECT-LINK-USEFUL-FOR-SCOUT',
'https://st.yandex-team.ru',
'elrusso',
'https://github.yandex-team.ru/taxi/backend-py3/blob/develop/admin-users-info/service.yaml'
),
(
2,
'envoy-exp-alpha',
'artifact_name',
'nanny',
'TAXIADMIN-9711',
'https://st.yandex-team.ru',
'https://wiki.yandex-team.ru',
'https://st.yandex-team.ru',
'abc_service',
'envoy-exp-alpha',
'envoy-exp-alpha',
'taxi_tst_envoy-exp-alpha-NOT-THE-DIRECT-LINK-USEFUL-FOR-SCOUT',
'https://st.yandex-team.ru',
'elrusso',
'https://github.yandex-team.ru/taxi/backend-py3/blob/develop/admin-users-info/service.yaml'
)
;

insert into clownductor.branches (
    service_id,
    name,
    env,
    direct_link,
    endpointsets
)
values
    (1, 'stable', 'stable', 'test_nanny_service', '[]'::jsonb),
    (1, 'testing', 'testing', 'test_nanny_service', '[]'::jsonb),
    (1, 'unstable', 'unstable', 'test_nanny_service', '[]'::jsonb),
    (1, 'pre_stable', 'prestable', 'test_nanny_service', '[]'::jsonb),
    (2, 'stable', 'stable', 'test_nanny_service', '[]'::jsonb),
    (2, 'testing', 'testing', 'test_nanny_service', '[]'::jsonb),
    (2, 'unstable', 'unstable', 'test_nanny_service', '[]'::jsonb),
    (2, 'pre_stable', 'prestable', 'test_nanny_service', '[]'::jsonb),
    (3, 'stable', 'stable', 'test_conductor_service', '[]'::jsonb),
    (4, 'envoy-exp-bravo', 'stable', 'taxi_tst_envoy-exp-bravo_stable',
        '[{"id":"taxi_envoy_exp_bravo_service_name_stable","regions":["MAN","SAS"]}]'::jsonb
    ),
    (5, 'envoy-exp-charlie', 'stable', 'taxi_tst_envoy-exp-charlie_stable',
        '[{"id":"taxi_envoy_exp_charlie_service_name_stable","regions":["MAN","SAS"]}]'::jsonb
    ),
    (6, 'envoy-exp-alpha', 'stable', 'taxi_tst_envoy-exp-alpha_stable',
        '[{"id":"taxi_envoy_exp_alpha_service_name_stable","regions":["MAN","SAS"]}]'::jsonb
    );

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
        '{"clownductor_project": "test", "service_type": "python3", "duty_group_id": "42"}'::jsonb,
        '{"clownductor_project": "test", "service_type": "python3", "duty_group_id": "42"}'::jsonb
    ),
    (
        'service_info', 1, 1,
        '{"grafana": "https://grafana.yandex-team.ru/d/LVu3OitWk/nanny_taxi_clownductor_stable", "duty_group_id" : "SERVICE_ilya_duty_1", "clownductor_project": "taxi"}'::jsonb,
        '{"grafana": "https://grafana.yandex-team.ru/d/LVu3OitWk/nanny_taxi_clownductor_stable", "duty_group_id" : "REMOTE_ilya_duty_22", "clownductor_project": "taxi_new"}'::jsonb
    ),
    (
        'nanny', 1, 1,
        '{"cpu": 1000, "ram": 1000, "root_size": 10240, "work_dir": 512, "instances": 1, "datacenters_count": 2, "persistent_volumes": [{"size": 10240, "path": "/logs", "type": "hdd", "bandwidth_guarantee_mb_per_sec": 3, "bandwidth_limit_mb_per_sec": 6}]}'::jsonb,
        '{"cpu": 1000, "ram": 1000, "root_size": 5120, "work_dir": 256, "instances": 1, "datacenters_count": 2}'::jsonb
    ),
    (
        'nanny', 1, 2,
        '{"cpu": 1000, "ram": 1000, "root_size": 10240, "work_dir": 512, "instances": 2, "datacenters_count": 2, "persistent_volumes": [{"size": 10240, "path": "/logs", "type": "hdd", "bandwidth_guarantee_mb_per_sec": 3, "bandwidth_limit_mb_per_sec": 6}]}'::jsonb,
        '{"cpu": 1000, "ram": 1000, "root_size": 10240, "work_dir": 512, "instances": 1, "datacenters_count": 1, "persistent_volumes": [{"size": 10240, "path": "/logs", "type": "hdd", "bandwidth_guarantee_mb_per_sec": 9, "bandwidth_limit_mb_per_sec": 12}]}'::jsonb
    ),
    (
        'nanny', 1, 3,
        '{"cpu": 1000, "ram": 1000, "root_size": 10240, "work_dir": 512, "instances": 1, "datacenters_count": 1}'::jsonb,
        '{"cpu": 500, "ram": 500, "root_size": 10240, "work_dir": 512, "instances": 1, "datacenters_count": 1}'::jsonb
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
        'abc', 2, 5,
        '{"maintainers": ["karachevda"]}'::jsonb,
        '{"maintainers": ["karachevda"]}'::jsonb
    ),
    (
        'nanny', 2, 5,
        '{"cpu": 1000, "root_size": 10240, "work_dir": 512, "ram": 1000, "instances": 1, "datacenters_count": 2}'::jsonb,
        '{"cpu": 1000, "root_size": 10240, "work_dir": 512, "ram": 1000, "instances": 1, "datacenters_count": 2}'::jsonb
    ),
    (
        'nanny', 2, 6,
        '{"cpu": 100, "root_size": 10, "work_dir": 512, "ram": 500, "instances": 1, "datacenters_count": 4, "persistent_volumes": null}'::jsonb,
        '{"cpu": 1000, "root_size": 5120, "work_dir": 512, "ram": 1000, "instances": 1, "datacenters_count": 1, "persistent_volumes": []}'::jsonb
    ),
    (
        'service_info', 3, 9,
        '{}'::jsonb,
        '{}'::jsonb
    ),
    (
        'service_info', 4, NULL,
        '{"hostnames": {"testing": ["envoy-exp-bravo.taxi.tst.yandex.net"], "production": ["envoy-exp-bravo.taxi.yandex.net"]}}'::jsonb,
        '{}'::jsonb
    ),
    (
        'service_info', 5, NULL,
        '{"hostnames": {"testing": ["envoy-exp-charlie.taxi.tst.yandex.net"], "production": ["envoy-exp-charlie.taxi.yandex.net"]}}'::jsonb,
        '{}'::jsonb
    );
