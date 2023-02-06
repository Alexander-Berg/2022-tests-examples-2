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
),
(
'taxi_infra',
'TAXI_TEST',
'TAXI_STAB:E',
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
'clownductor',
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
), (
1,
'service_2',
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
), (
1,
'service_3',
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
), (
1,
'service_without_unstable',
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
'https://a.yandex-team.ru/arc_vcs/taxi/backend-py3/services/clownductor/service.yaml'
);

insert into clownductor.branches (
    service_id,
    name,
    env,
    direct_link
)
values
    (1, 'stable', 'stable', ''),
    (1, 'testing', 'testing', ''),
    (1, 'unstable', 'unstable', ''),
    (1, 'pre_stable', 'prestable', ''),
    (2, 'stable', 'stable', ''),
    (2, 'testing', 'testing', ''),
    (2, 'unstable', 'unstable', ''),
    (2, 'pre_stable', 'prestable', ''),
    (3, 'stable', 'stable', ''),
    (1, 'testing_without_parameters', 'testing', ''),
    (4, 'testing', 'testing', ''),
    (4, 'testing_2', 'testing', '')
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
        '{"clownductor_project": "test", "service_type": "python3"}'::jsonb,
        '{"clownductor_project": "test", "service_type": "python3"}'::jsonb
    ),
    (
        'nanny', 1, 1,
        '{"cpu": 1000, "ram": 1024, "instances": 1, "root_size": 10240, "work_dir": 512, "datacenters_count": 2, "root_storage_class": "hdd"}'::jsonb,
        '{"cpu": 1000, "ram": 1024, "instances": 1, "root_size": 10240, "work_dir": 512, "datacenters_count": 2, "root_storage_class": "ssd"}'::jsonb
    ),
    (
        'nanny', 1, 2,
        '{"cpu": 1000, "ram": 1024, "instances": 1, "root_size": 10240, "work_dir": 512, "datacenters_count": 2, "root_storage_class": "hdd"}'::jsonb,
        '{"cpu": 1000, "ram": 1024, "instances": 1, "root_size": 10240, "work_dir": 512, "datacenters_count": 1, "root_storage_class": "ssd"}'::jsonb
    ),
    (
        'nanny', 1, 3,
        '{"cpu": 1000, "ram": 1024, "instances": 1, "root_size": 10240, "work_dir": 512, "datacenters_count": 1}'::jsonb,
        '{"cpu": 500, "ram": 512, "instances": 1, "root_size": 10240, "work_dir": 512, "datacenters_count": 1}'::jsonb
    ),
    (
        'abc', 1, 1,
        '{"maintainers": ["karachevda", "meow"]}'::jsonb,
        '{"maintainers": ["kus", "karachevda"]}'::jsonb
    ),
    (
        'abc', 2, 5,
        '{"maintainers": ["karachevda"]}'::jsonb,
        '{"maintainers": ["karachevda"]}'::jsonb
    ),
    (
        'service_info', 3, 9,
        '{"service_type": "python3"}'::jsonb,
        '{"service_type": "python3"}'::jsonb
    ),
    (
        'nanny', 4, 12,
        '{"cpu": 1000, "ram": 1024, "instances": 1, "root_size": 10240, "work_dir": 512, "datacenters_count": 2, "root_storage_class": "hdd"}'::jsonb,
        '{"cpu": 1000, "ram": 1024, "instances": 1, "root_size": 10240, "work_dir": 512, "datacenters_count": 1, "root_storage_class": "ssd"}'::jsonb
    ),
    (
        'service_info', 1, 2,
        '{"clownductor_project": "taxi", "service_type": "python3"}'::jsonb,
        '{"clownductor_project": "taxi_infra", "service_type": "python3"}'::jsonb
    );


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
    'ResolveServiceDiff',
    'elrusso',
    'in_progress'
)
;
