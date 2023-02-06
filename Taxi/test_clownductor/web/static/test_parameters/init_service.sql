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
'taxi_new',
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
null
),(
1,
'admin-users-info',
'artifact_name',
'conductor',
'https://st.yandex-team.ru',
'https://st.yandex-team.ru',
'abc_service',
'tvm_testing_abc_service',
'tvm_stable_abc_service',
'https://st.yandex-team.ru',
'https://st.yandex-team.ru',
'elrusso',
'https://github.yandex-team.ru/taxi/backend-py3/blob/develop/admin-users-info/service.yaml'
),(
1,
'test-service-4',
'artifact_name',
'nanny',
'https://st.yandex-team.ru',
'https://st.yandex-team.ru',
'abc_service',
'tvm_testing_abc_service',
'tvm_stable_abc_service',
'https://st.yandex-team.ru',
'https://st.yandex-team.ru',
'd1mbas',
null
),(
1,
'test-service-5',
'artifact_name',
'nanny',
'https://st.yandex-team.ru',
'https://st.yandex-team.ru',
'abc_service',
'tvm_testing_abc_service',
'tvm_stable_abc_service',
'https://st.yandex-team.ru',
'https://st.yandex-team.ru',
'd1mbas',
null
),(
1,
'test-service-6',
'artifact_name',
'nanny',
'https://st.yandex-team.ru',
'https://st.yandex-team.ru',
'abc_service',
'tvm_testing_abc_service',
'tvm_stable_abc_service',
'https://st.yandex-team.ru',
'https://st.yandex-team.ru',
'd1mbas',
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
    (1, 'stable', 'stable', 'test_nanny_service'),
    (1, 'testing', 'testing', 'test_nanny_service'),
    (1, 'unstable', 'unstable', 'test_nanny_service'),
    (1, 'pre_stable', 'prestable', 'test_nanny_service'),
    (2, 'stable', 'stable', 'test_nanny_service'),
    (2, 'testing', 'testing', 'test_nanny_service'),
    (2, 'unstable', 'unstable', 'test_nanny_service'),
    (2, 'pre_stable', 'prestable', 'test_nanny_service'),
    (3, 'stable', 'stable', 'test_conductor_service'),
    (4, 'branch-10', 'stable', 'taxi_test-service-4_stable-10'),
    (4, 'branch-11', 'stable', 'taxi_test-service-4_stable-11'),
    (4, 'branch-12', 'stable', 'taxi_test-service-4_stable-12'),
    (5, 'branch-13', 'stable', 'taxi_test-service-5_stable-13'),
    (5, 'branch-14', 'testing', 'taxi_test-service-5_stable-14'),
    (6, 'branch-15', 'stable', 'taxi_test-service-6_stable-15'),
    (6, 'branch-16', 'stable', 'taxi_test-service-6_stable-16'),
    (6, 'branch-17', 'stable', 'taxi_test-service-6_stable-17');

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
        '{"clownductor_project": "test", "service_type": "python3", "duty_group_id": "42", "critical_class": "A"}'::jsonb,
        '{"clownductor_project": "test", "service_type": "python3", "duty_group_id": "42", "critical_class": "A"}'::jsonb
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
        'awacs', 1, 1,
        '{}'::jsonb,
        '{}'::jsonb
    ),
    (
        'nanny', 1, 2,
        '{"cpu": 1000, "ram": 1000, "root_size": 10240, "work_dir": 512, "instances": 2, "datacenters_count": 2, "persistent_volumes": [{"size": 10240, "path": "/logs", "type": "hdd", "bandwidth_guarantee_mb_per_sec": 3, "bandwidth_limit_mb_per_sec": 6}]}'::jsonb,
        '{"cpu": 1000, "ram": 1000, "root_size": 10240, "work_dir": 512, "instances": 1, "datacenters_count": 1, "persistent_volumes": [{"size": 10240, "path": "/logs", "type": "hdd", "bandwidth_guarantee_mb_per_sec": 9, "bandwidth_limit_mb_per_sec": 12}]}'::jsonb
    ),
    (
        'awacs', 1, 2,
        '{}'::jsonb,
        '{}'::jsonb
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
        'service_info', 4, 10,
        '{"duty": {"abc_slug": "some_service", "primary_schedule": "non-existing-schedule"}}'::jsonb,
        '{}'::jsonb
    ),
    (
        'service_info', 4, 11,
        '{"duty": {"abc_slug": "some_service", "primary_schedule": "existing-schedule"}}'::jsonb,
        '{}'::jsonb
    ),
    (
        'nanny', 4, 12,
        '{"cpu": 100, "root_size": 1024, "work_dir": 512, "ram": 512, "instances": 1, "datacenters_count": 2, "datacenters_regions": ["vla", "sas"], "persistent_volumes": null}'::jsonb,
        '{"cpu": 100, "root_size": 1024, "work_dir": 512, "ram": 512, "instances": 1, "datacenters_count": 2, "datacenters_regions": ["vla"], "persistent_volumes": null}'::jsonb
    ),
    (
        'nanny', 5, 13,
        '{"cpu": 100, "root_size": 1024, "work_dir": 512, "ram": 512, "instances": 1, "datacenters_count": 2, "datacenters_regions": null}'::jsonb,
        '{"cpu": 100, "root_size": 1024, "work_dir": 512, "ram": 512, "instances": 1, "datacenters_count": 2, "datacenters_regions": ["vla", "sas"]}'::jsonb
    ),
    (
        'awacs', 5, 13,
        '{"cpu": 1000, "datacenters_instances": { "man": 1, "sas": 1, "vla": 1}, "persistent_volumes": [{"bandwidth_guarantee_mb_per_sec": 1, "bandwidth_limit_mb_per_sec": 1, "path": "/logs", "size": 10240, "storage_class": "hdd"}, {"bandwidth_guarantee_mb_per_sec": 1, "bandwidth_limit_mb_per_sec": 1, "path": "/awacs", "size": 120, "storage_class": "hdd"}], "ram": 2048, "root_volume": {"bandwidth_guarantee_mb_per_sec": 1, "bandwidth_limit_mb_per_sec": 1, "path": "/", "size": 512, "storage_class": "hdd"}}'::jsonb,
        '{}'::jsonb
    ),
    (
        'nanny', 5, 14,
        '{"cpu": 100, "root_size": 1024, "work_dir": 512, "ram": 512, "instances": 1, "datacenters_count": 2, "datacenters_regions": ["vla", "sas"]}'::jsonb,
        '{"cpu": 100, "root_size": 1024, "work_dir": 512, "ram": 512, "instances": 1, "datacenters_count": 3, "datacenters_regions": ["vla", "sas", "man"]}'::jsonb
    ),
        (
        'nanny', 6, 15,
        '{"cpu": 100, "root_size": 1024, "work_dir": 512, "ram": 512, "instances": 1, "datacenters_count": 2, "datacenters_regions": ["man", "sas"]}'::jsonb,
        '{"cpu": 100, "root_size": 1024, "work_dir": 512, "ram": 512, "instances": 1, "datacenters_count": 2, "datacenters_regions": ["vla", "sas"]}'::jsonb
    ),
    (
        'nanny', 6, 16,
        '{"cpu": 100, "root_size": 1024, "work_dir": 512, "ram": 512, "instances": 1, "datacenters_count": 2, "datacenters_regions": ["vla", "sas"]}'::jsonb,
        '{"cpu": 100, "root_size": 1024, "work_dir": 512, "ram": 512, "instances": 1, "datacenters_count": 3, "datacenters_regions": ["vla", "sas", "man"]}'::jsonb
    )
   ;
