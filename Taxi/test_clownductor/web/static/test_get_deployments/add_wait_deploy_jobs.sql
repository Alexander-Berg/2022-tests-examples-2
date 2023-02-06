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
'test_service2',
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
2,
'unstable_branch',
'unstable',
''
), (
2,
'testing_branch',
'testing',
''
), (
2,
'stable_branch',
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
2,
4,
'WaitMainDeployNannyServiceNoApprove',
'deoevgen',
'canceled',
5
), (
2,
5,
'WaitMainDeployNannyServiceWithApprove',
'deoevgen',
'success',
6
), (
2,
6,
'WaitMainDeployNannyServiceWithApprove',
'deoevgen',
'success',
7
), (
2,
4,
'WaitMainDeployNannyServiceNoApprove',
'deoevgen',
'in_progress',
8
), (
2,
4,
'WaitMainDeployNannyServiceNoApprove',
'deoevgen',
'success',
9
)
;

insert into
task_manager.job_variables (
job_id,
variables
)
values (
4,
'{"job_id": 1, "name": "WaitMainDeployNannyServiceNoApprove", "image": "image_name", "comment": "test comment", "sandbox_resources": null}'
), (
5,
'{"job_id": 2, "name": "WaitMainDeployNannyServiceWithApprove", "image": "image_name", "comment": "test comment", "sandbox_resources": null}'
), (
6,
'{"job_id": 3, "name": "WaitMainDeployNannyServiceWithApprove", "image": "image_name", "comment": "test comment", "sandbox_resources": null}'
),
-- waiting jobs without link on main deploy job
(
7,
'{"job_id": null, "name": "WaitMainDeployNannyServiceNoApprove", "image": "image_name", "comment": "test comment", "sandbox_resources": null}'
), (
8,
'{"name": "WaitMainDeployNannyServiceNoApprove", "image": "image_name", "comment": "test comment", "sandbox_resources": null}'
)
;
