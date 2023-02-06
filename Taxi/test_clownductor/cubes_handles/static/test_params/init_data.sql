insert into clownductor.namespaces (name) values ('taxi');

insert into clownductor.projects (
    name,
    network_testing,
    network_stable,
    service_abc,
    yp_quota_abc,
    tvm_root_abc,
    responsible_team,
    namespace_id
)
values (
    'test_project',
    '_TAXITESTNETS_',
    '_HWTAXINETS_',
    'taxiservicesdeploymanagement',
    'taxiquotaypdefault',
    'taxitvmaccess',
    '{"ops": ["yandex_rkub_taxi_5151_8501_9282_dep50822"], "managers": [], "developers": [], "superusers": ["isharov", "nikslim"]}',
    1
), (
    'taxi',
    '_TAXITESTINFRA_',
    '_HWTAXINETS_',
    'taxiservicesdeploymanagement',
    'taxiquotaypdefault',
    'taxitvmaccess',
    '{"ops": ["yandex_rkub_taxi_5151_8501_9282_dep50822"], "managers": [], "developers": [], "superusers": ["isharov", "nikslim"]}',
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
    direct_link,
    service_url
)
values (
    1,
    'test_service',
    'taxi/test_service/$',
    'nanny',
    'unit_test',
    'abc_service',
    null,
    null
), (
    2,
    'some_service',
    'taxi/some_service/$',
    'nanny',
    'unit_test',
    'abc_service',
    'test_direct',
    null
), (
    1,
    'test_yaml_generate',
    'taxi/test_yaml_generate/$',
    'nanny',
    'unit_test',
    'abc_service',
    null,
    'https://github.yandex-team.ru/taxi/uservices/blob/develop/services/route-calc/service.yaml'
), (
    2,
    'service-4',
    'taxi/service-4/$',
    'nanny',
    'requester',
    'taxiservice4',
    'taxi_service-4',
    'https://a.yandex-team.ru/arc_vcs/taxi/backend-py3/services/service-4/service.yaml'
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
    'unstable_branch_1',
    'unstable',
    'test_service_unstable'
), (
    2,
    'unstable_branch_2',
    'unstable',
    'path'
), (
    1,
    'prestable_branch_1',
    'prestable',
    'path'
), (
    1,
    'prestable_branch_2',
    'stable',
    'path_test'
), (
    3,
    'unstable_branch_5',
    'unstable',
    'test_service_unstable'
), (
    3,
    'unstable_branch_6',
    'unstable',
    'test_service_unstable'
), (
    4,
    'stable',
    'stable',
    'taxi_service-4_stable'
)
;

insert into clownductor.parameters (
    subsystem_name,
    service_id,
    branch_id,
    service_values,
    remote_values
)
values
    ('service_info', 1, 4, '{"duty": {"abc_slug": "existing-service", "primary_schedule": "existing-schedule"}}'::jsonb, '{"duty_group_id": "1b69be79c5755f678048a169"}'::jsonb),
    ('nanny', 1, 4, '{"root_storage_class": "ssd", "cpu": 1000}'::jsonb, '{"root_storage_class": "hdd", "cpu": 1000}'::jsonb),
    ('nanny', 3, 6,
     '{"root_storage_class": "ssd", "cpu": 14000, "ram": 16384, "work_dir": 256, "instances": 2, "root_size": 10240, "datacenters_count": 1, "persistent_volumes": [{"path": "/cores", "size": 10240, "type": "ssd"}, {"path": "/logs", "size": 500000, "type": "ssd"}, {"path": "/var/cache/yandex", "size": 2048, "type": "ssd"}]}'::jsonb,
     '{"root_storage_class": "hdd", "cpu": 1000, "ram": 163840, "work_dir": 256, "instances": 3, "root_size": 10240, "datacenters_count": 2, "persistent_volumes": [{"path": "/cores", "size": 10240, "type": "ssd"}, {"path": "/logs", "size": 500000, "type": "ssd"}, {"path": "/var/cache/yandex", "size": 2048, "type": "ssd"}]}'::jsonb),
    ('service_info', 4, 7, '{"duty": {"abc_slug": "service4", "primary_schedule": "primaryschedule"}}'::jsonb, '{"duty_group_id": "1b69be79c5755f678048a169"}'::jsonb)
;
