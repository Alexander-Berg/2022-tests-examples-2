insert into clownductor.namespaces (name) values ('taxi');

INSERT INTO clownductor.projects (
    name,
    network_testing,
    network_stable,
    service_abc,
    yp_quota_abc,
    tvm_root_abc,
    owners,
    env_params,
    namespace_id
)
VALUES (
    'test_project',
    '_TAXITESTNETS_',
    '_HWTAXINETS_',
    'taxiservicesdeploymanagement',
    'taxiquotaypdefault',
    'taxitvmaccess',
    '{"groups": ["elrusso_group"], "logins": ["elrusso"]}'::jsonb,
    '{"stable": {"domain": "taxi.yandex.net"}, "general": {"project_prefix": "taxi", "docker_image_tpl": "taxi/{{ service }}/$"}, "testing": {"domain": "taxi.tst.yandex.net"}, "unstable": {"domain": "taxi.dev.yandex.net"}}'::jsonb,
    1
)
;

insert into clownductor.services (
    project_id,
    name,
    artifact_name,
    cluster_type,
    requester,
    abc_service,
    direct_link
)
values (
    1,
    'test_service',
    'taxi/test_service/$',
    'nanny',
    'unit_test',
    'abc_service',
    'test-service'
)
;

insert into clownductor.branches (
    service_id,
    name,
    env,
    direct_link
)
values (
    1,
    'unstable_branch',
    'unstable',
    'test_service_unstable'
),
(
    1,
    'testing',
    'testing',
    'test_service_testing'
);

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

