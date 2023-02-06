insert into clownductor.namespaces (name) values ('taxi'), ('eda');

insert into clownductor.projects (
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

insert into clownductor.services (
    project_id,
    name,
    artifact_name,
    cluster_type,
    requester,
    abc_service,
    service_url
)
values (
    1,
    'candidates',
    'taxi/candidates/$',
    'nanny',
    'unit_test',
    'abc_service',
    'https://github.yandex-team.ru/taxi/uservices/blob/develop/services/test_service/service.yaml'
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
    'unstable',
    'unstable',
    'test_service_unstable'
),(
    1,
    'stable',
    'stable',
    'test_service_stable'
)
;

insert into task_manager.jobs (
    service_id,
    branch_id,
    name,
    initiator,
    status,
    change_doc_id
)
values (
    1,
    2,
    'DeployNannyServiceWithApprove',
    'azhuchkov',
    'in_progress',
    'DeployNannyServiceWithApprove-1-2-deploy_type=sandbox'
), (
    1,
    2,
    'DeployNannyServiceWithApprove',
    'azhuchkov',
    'in_progress',
    'DeployNannyServiceWithApprove-1-2-deploy_type=code'
)
;

insert into
    task_manager.job_variables (
    job_id,
    variables
)
values (
    1,
    '{"name": "DeployNannyServiceWithApprove", "image": null, "comment": "test comment", "sandbox_resources": [
      {
        "local_path": "/some/path",
        "resource_id": "resource_id_1",
        "resource_type": "resource_type",
        "task_id": "task_id_1",
        "task_type": "task_type"
      }
    ], "release_ticket_st": "TAXIREL-13"}'
),(
    2,
    '{"name": "DeployNannyServiceNoApprove", "image": "taxi/candidates/production:0.0.296", "comment": "test comment", "release_ticket_st": "TAXIREL-13", "sandbox_resources": null}'
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
    (
        'nanny', 1, 2,
        '{"cpu": 1000}'::jsonb,
        '{"cpu": 1000}'::jsonb
    );


insert into task_manager.locks (name, job_id)
values ('Deploy.test_service_stable', 1)
;
