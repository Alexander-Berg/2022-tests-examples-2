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
    'artifact_name',
    'nanny',
    'unit_test',
    'abc_service'
), (
    1,
    'test_service_2',
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
    'unstable_branch',
    'unstable',
    ''
), (
    1,
    'testing_branch',
    'testing',
    ''
), (
    1,
    'stable_branch',
    'stable',
    ''
), (
    2,
    'unstable_branch_2',
    'unstable',
    ''
), (
    2,
    'testing_branch_2',
    'testing',
    ''
), (
    2,
    'stable_branch_2',
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
    'deoevgen',
    'canceled',
    1597000000
), (
    1,
    2,
    'DeployNannyServiceNoApprove',
    'deoevgen',
    'success',
    1597000000
),
(
    2,
    4,
    'DeployNannyServiceNoApprove',
    'karachevda',
    'in_progress',
    1597000000
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
)
;

insert into
    task_manager.tasks (
        id, job_id, name, input_mapping, output_mapping, status, created_at, updated_at
    )
values
    (1, 1, 'InternalGetLock', '{"lock_name": "lock_name"}', '{}', 'success', 1597000000, 1597000000),
    (2, 1, 'task2', '{}', '{}', 'success', 1597000000, 1597000000),
    (3, 3, 'task3', '{}', '{}', 'success', 1597000000, 1597000000)
;
