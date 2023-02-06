insert into clownductor.namespaces (name) values ('taxi');

insert into
clownductor.projects (
name,
network_testing,
network_stable,
service_abc,
yp_quota_abc,
tvm_root_abc,
namespace_id
)
values (
    'test_project',
    '_TAXITESTNETS_',
    '_HWTAXINETS_',
    'taxiservicesdeploymanagement',
    'taxiquotaypdefault',
    'taxitvmaccess',
    1
)
;

insert into
clownductor.services (
project_id,
name,
artifact_name,
cluster_type,
requester,
abc_service
)
values (
    1,
    'service_main',
    'artifact_name',
    'nanny',
    'unit_test',
    'abc_service'
),(
    1,
    'service_slave',
    'artifact_name',
    'nanny',
    'unit_test',
    'abc_service'
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
    'stable_main',
    'stable',
    ''
),(
    2,
    'stable_slave',
    'stable',
    ''
)
;

insert into task_manager.jobs (
service_id,
branch_id,
name,
initiator,
status,
created_at
)
values (
    1,
    1,
    'DeployNannyServiceNoApprove',
    'elrusso',
    'success',
    3
),(
    2,
    2,
    'WaitMainDeployNannyServiceNoApprove',
    'elrusso',
    'success',
    4
)
;

insert into
task_manager.job_variables (
job_id,
variables
)
values (
    1,
    '{"job_service_id": 1, "job_branch_id": 1, "name": "DeployNannyServiceNoApprove", "image": "image_name", "aliases": [{"service_id": 1, "branch_id": 1, "nanny_name": "stable_main", "image": "image1"}, {"service_id": 2, "branch_id": 2, "nanny_name": "stable_slave", "image": "image2"}], "comment": "test comment", "prestable_name": "prestabe_name_test", "release_ticket_st": "release_ticket_st", "approving_managers": [], "approving_developers": [], "sandbox_resources": null}'
),(
    2,
    '{"job_id": 1}'
)

;
