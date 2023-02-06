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
'test_service',
'artifact_name/$',
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
'unstable_name',
'unstable',
''
), (
1,
'testing',
'testing',
''
), (
1,
'stable',
'stable',
''
)
;

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
'DeployNannyServiceNoApprove',
'deoevgen',
'canceled'
), (
1,
2,
'DeployNannyServiceNoApprove',
'deoevgen',
'canceled'
), (
1,
3,
'DeployNannyServiceWithApprove',
'deoevgen',
'in_progress'
), (
1,
3,
'CreateFullNannyService',
'deoevgen',
'in_progress'
)
;

insert into
task_manager.job_variables (
job_id,
variables
)
values (
1,
'{"name": "DeployNannyServiceNoApprove", "image": "image_name", "comment": "test comment", "sandbox_resources": null}'
), (
2,
'{"name": "DeployNannyServiceNoApprove", "image": "image_name", "comment": "test comment", "sandbox_resources": null}'
), (
3,
'{"name": "DeployNannyServiceNoApprove", "image": "image_name", "comment": "test comment", "prestable_name": "prestabe_name_test", "release_ticket_st": "release_ticket_st", "approving_managers": [], "approving_developers": [], "sandbox_resources": null}'
), (
4,
'{}'
)
;
