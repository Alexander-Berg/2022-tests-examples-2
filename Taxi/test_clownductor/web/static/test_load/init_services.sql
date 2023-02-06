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
    'dyusudakov',
    'https://github.yandex-team.ru/taxi/backend-py3/blob/develop/services/clownductor/service.yaml'
),(
    1,
    'test_service_two',
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
),
(
    1,
    'another_test_service',
    'artifact_name',
    'nanny',
    'https://st.yandex-team.ru',
    'https://st.yandex-team.ru',
    'abc_service',
    'tvm_testing_abc_service',
    'tvm_stable_abc_service',
    'https://st.yandex-team.ru',
    'https://st.yandex-team.ru',
    'dyusudakov',
    'https://a.yandex-team.ru/arc_vcs/taxi/backend-py3/services/clownductor/service.yaml'
)
;

insert into
    clownductor.branches (
        service_id,
        name,
        env,
        direct_link
    )
values (
    1,
    'stable_branch',
    'stable',
    'test-service-1-direct'
), (
    1,
    'testing_branch',
    'testing',
    'test-service-1-direct-testing'
), (
    1,
    'tank_branch',
    'testing',
    'test-service-1-tank-testing'
)
;

insert into clownductor.parameters (
  subsystem_name, 
  service_id, 
  branch_id, 
  service_values, 
  remote_values
) values (
  'nanny', 
  1, 
  2, 
  '{"cpu": 1000, "ram": 1000, "root_size": 10240, "work_dir": 512, "instances": 2, "datacenters_count": 2, "persistent_volumes": [{"size": 10240, "path": "/logs", "type": "hdd"}]}'::jsonb,
  '{"cpu": 1000, "ram": 1000, "root_size": 10240, "work_dir": 512, "instances": 2, "datacenters_count": 2, "persistent_volumes": [{"size": 10240, "path": "/logs", "type": "hdd"}]}'::jsonb
)
;
