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
    'lavka',
    '_TAXITESTNETS_',
    '_HWTAXINETS_',
    'taxiservicesdeploymanagement',
    'taxiquotaypdefault',
    'taxitvmaccess',
    1
),(
    'eda',
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
    'lavka-service',
    'artifact_name',
    'nanny',
    'unit_test',
    'abc_service'
),
(
    2,
    'eda-service',
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
    env,
    direct_link
)
VALUES (
    1,
    'unstable_branch_lavka',
    'unstable',
    'unstable'
),
       (
    2,
    'unstable_branch_eda',
    'unstable',
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
    'DeployNannyServiceNoApprove',
    'azhuchkov',
    'in_progress',
    null,
    'DeployNannyServiceNoApprove_1_1',
    'DeployNannyServiceNoApprove_1',
    1510668800
),
(
    1,
    1,
    'DeployOneNannyService',
    'azhuchkov',
    'in_progress',
    null,
    'DeployOneNannyService_1_1',
    'DeployOneNannyService_1',
    1510668800
),
(
    2,
    2,
    'DeployNannyServiceNoApprove',
    'azhuchkov',
    'in_progress',
    null,
    'DeployNannyServiceNoApprove_2_2',
    'DeployNannyServiceNoApprove_2',
    1510668800
),
(
    2,
    2,
    'DeployOneNannyService',
    'azhuchkov',
    'in_progress',
    null,
    'DeployOneNannyService_2_2',
    'DeployOneNannyService_2',
    1510668800
)
;
