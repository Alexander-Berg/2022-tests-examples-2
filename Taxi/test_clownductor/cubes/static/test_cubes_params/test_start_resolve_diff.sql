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
    'test_yaml_generate',
    'taxi/test_yaml_generate/$',
    'nanny',
    'unit_test',
    'abc_service',
    null,
    'https://github.yandex-team.ru/taxi/uservices/blob/develop/services/route-calc/service.yaml'
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
    1,
    'unstable_branch_2',
    'testing',
    'test_service_testing'
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
    'deoevgen',
    'canceled'
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
    ('service_info', 1, 1, '{"duty_group_id": "1b69be79c5755f678048a169"}'::jsonb, '{"duty_group_id": "1b69be79c5755f678048a169"}'::jsonb),
    ('nanny', 1, 1, '{"cpu": 1000}'::jsonb, '{"cpu": 1000}'::jsonb),
    ('nanny', 1, 2, '{"cpu": 1000, "root_storage_class": "hdd"}'::jsonb, '{"cpu": 14000, "root_storage_class": "ssd","ram": 163840, "work_dir": 256, "instances": 3, "root_size": 10240, "datacenters_count": 2, "persistent_volumes": [{"path": "/cores", "size": 10240, "type": "ssd"}, {"path": "/logs", "size": 500000, "type": "ssd"}, {"path": "/var/cache/yandex", "size": 2048, "type": "ssd"}]}'::jsonb)
;
