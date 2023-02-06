insert into clownductor.namespaces (name) values ('taxi');

INSERT INTO
clownductor.projects (
    name,
    network_testing,
    network_stable,
    service_abc,
    yp_quota_abc,
    tvm_root_abc,
    namespace_id
)
VALUES (
    'test_project',
    '_TAXITESTNETS_',
    '_HWTAXINETS_',
    'taxiservicesdeploymanagement',
    'taxiquotaypdefault',
    'taxitvmaccess',
    1
)
;

INSERT INTO
clownductor.services (
    project_id,
    name,
    artifact_name,
    cluster_type,
    requester,
    abc_service
)
VALUES (
    1,
    'taxi',
    'artifact_name',
    'nanny',
    'unit_test',
    'abc_service'
),
(
    1,
    'taxi-2-service',
    'artifact_name',
    'nanny',
    'unit_test',
    'abc_service'
)
;

INSERT INTO
clownductor.branches (
    service_id,
    name,
    env
)
VALUES (
    1,
    'unstable_branch',
    'unstable'
)
;

INSERT INTO task_manager.jobs (
    service_id,
    branch_id,
    name,
    initiator,
    status,
    remote_job_id,
    tp_change_doc_id,
    tp_token,
    created_at
)
VALUES (
    1,
    1,
    'MyJobName1',
    'deoevgen',
    'in_progress',
    null,
    'DeployNannyServiceNoApprove_1_1',
    'DeployNannyServiceNoApprove_1',
    1558959851
),
(
    2,
    1,
    'MyJobName2',
    'deoevgen',
    'in_progress',
    null,
    'DeployNannyServiceNoApprove_2_2',
    'DeployNannyServiceNoApprove_2',
    1558959851
),
(
    1,
    1,
    'MyJobName3',
    'deoevgen',
    'inited',
    null,
    'DeployNannyServiceNoApprove_3_3',
    'DeployNannyServiceNoApprove_3',
    1558959851
)
;

INSERT INTO
task_manager.job_variables (
job_id,
variables
)
VALUES (
1,
'{"name": "DeployNannyServiceNoApprove", "image": "image_name", "user": "elrusso", "comment": "test comment",  "release_ticket_st": "ticket_name"}'
), (
2,
'{"name": "DeployNannyServiceNoApprove", "image": "image_name", "comment": "test comment",  "new_service_ticket": "ticket_name", "release_ticket_st": null}'
), (
3,
'{"name": "DeployNannyServiceNoApprove", "image": "image_name", "comment": "test comment", "prestable_name": "prestabe_name_test", "release_ticket_st": "ticket_name", "approving_managers": [], "approving_developers": []}'
)
;
