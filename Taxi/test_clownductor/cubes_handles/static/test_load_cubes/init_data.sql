insert into clownductor.namespaces (name) values ('taxi');

insert into clownductor.projects (
    id,
    name,
    network_testing,
    network_stable,
    service_abc,
    yp_quota_abc,
    tvm_root_abc,
    owners,
    namespace_id
)
values (
    1,
    'test_project',
    '_TAXITESTNETS_',
    '_HWTAXINETS_',
    'taxiservicesdeploymanagement',
    'taxiquotaypdefault',
    'taxitvmaccess',
    '{"groups": [], "logins": []}'::jsonb,
    1
)
;

insert into clownductor.services (
    id,
    project_id,
    name,
    artifact_name,
    cluster_type,
    requester,
    abc_service
)
values (
    1,
    1,
    'test_service',
    'taxi/test_service/$',
    'nanny',
    'unit_test',
    'abc_service'
)
;

insert into clownductor.branches (
    id,
    service_id,
    name,
    env,
    direct_link
)
values (
    1,
    1,
    'testing_branch',
    'testing',
    'test_service_testing'
)
;

insert into clownductor.hosts (
  name, 
  branch_id, 
  datacenter
)
values (
    'taxi-userver-load-tank-1.vla.yp-c.yandex.net',
    1,
    'vla'
),(
    'taxi-userver-load-tank-1.sas.yp-c.yandex.net',
    1,
    'sas'
)
;
