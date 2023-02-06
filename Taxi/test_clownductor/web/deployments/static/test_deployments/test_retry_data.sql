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
values
(
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
values
(
    1,
    'test_service',
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
values
(
    1,
    'unstable_branch',
    'unstable',
    ''
),(
    1,
    'testing_branch',
    'testing',
    ''
),(
    1,
    'prestable_branch',
    'prestable',
    'prestable_direct_link'
),(
    1,
    'stable_branch',
    'stable',
    'stable_direct_link'
)
;

insert into task_manager.jobs (
    service_id,
    branch_id,
    name,
    initiator,
    status
)
values
(
    1,
    4,
    'NotDeployJobName',
    'Elrusso',
    'in_progress'
),
(
    1,
    4,
    'DeployNannyServiceWithApprove',
    'elrusso',
    'success'
),
(
    1,
    4,
    'DeployNannyServiceWithApprove',
    'elrusso',
    'in_progress'
),(
    1,
    4,
    'DeployNannyServiceWithApprove',
    'elrusso',
    'in_progress'
);

insert into
task_manager.job_variables (
job_id,
variables
)
values
(
    1,
    '{}'
),
(
    2,
    '{"name": "DeployNannyServiceWithApprove", "release_ticket_st": "TAXIREL-1", "lock_names": ["Deploy.test_service_stable"], "image": "taxi/existing-service/stable:1.0.0", "comment": "image deplpy comment", "prestable_name": "prestabe_name_test", "sandbox_resources": null, "project_names": ["test_project"]}'
),(
    3,
    '{"name": "DeployNannyServiceWithApprove", "release_ticket_st": "TAXIREL-2", "lock_names": ["Deploy.test_service_stable"], "image": "taxi/existing-service/stable:1.0.1", "comment": "image deplpy comment", "prestable_name": "prestabe_name_test", "sandbox_resources": null, "project_names": ["test_project"]}'
), (
    4,
    '{"name": "DeployNannyServiceWithApprove", "release_ticket_st": "TAXIREL-2", "lock_names": ["Deploy.test_service_stable"], "comment": "sandbox deploy comment", "image": null, "prestable_name": "prestabe_name_test","sandbox_resources": [{"is_dynamic": false, "local_path": "road-graph", "resource_id": "1", "resource_type": "TAXI_GRAPH_ROAD_GRAPH_RESOURSE", "task_id": "745057883", "task_type": "TAXI_GRAPH_DO_UPLOAD_TASK"}], "project_names": ["test_project"]}'
);

insert into task_manager.locks (name, job_id)
values
(
    'Deploy.test_service_stable', 4
);
