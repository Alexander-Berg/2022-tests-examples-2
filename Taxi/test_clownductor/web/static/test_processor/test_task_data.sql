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
    '_taxitestnets_',
    '_hwtaxinets_',
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
    'test-service',
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
    'stable_branch',
    'stable',
    'test-service-1-direct'
)
;

insert into
    task_manager.jobs (
        service_id,
        branch_id,
        name,
        initiator,
        status
    )
values
    (1, 1, 'HighJob1', 'karachevda', 'canceled'),
    (1, 1, 'HighJob2', 'karachevda', 'failed'),
    (1, 1, 'HighJob1', 'karachevda', 'in_progress'),
    (1, 1, 'HighJob2', 'karachevda', 'in_progress'),
    (1, 1, 'HighJob2', 'karachevda', 'in_progress'),

    (1, 1, 'HighJob2', 'karachevda', 'in_progress'),
    (1, 1, 'HighJob1', 'karachevda', 'in_progress'),
    (1, 1, 'MiddleJob8', 'karachevda', 'in_progress'),
    (1, 1, 'MiddleJob9', 'karachevda', 'in_progress'),
    (1, 1, 'MiddleJob10', 'karachevda', 'in_progress'),

    (1, 1, 'MiddleJob11', 'karachevda', 'in_progress'),
    (1, 1, 'MiddleJob12', 'karachevda', 'in_progress'),
    (1, 1, 'LowJob1', 'karachevda', 'in_progress'),
    (1, 1, 'LowJob2', 'karachevda', 'in_progress'),
    (1, 1, 'LowJob3', 'karachevda', 'in_progress'),

    (1, 1, 'LowJob1', 'karachevda', 'in_progress'),
    (1, 1, 'LowJob2', 'karachevda', 'in_progress')
;

insert into
    task_manager.tasks (
        job_id,
        name,
        input_mapping,
        output_mapping,
        status
    )
values
    (1, 'HighTask1', '{}'::jsonb, '{}'::jsonb, 'canceled'),
    (2, 'HighTask2', '{}'::jsonb, '{}'::jsonb, 'failed'),
    (3, 'HighTask1', '{}'::jsonb, '{}'::jsonb, 'in_progress'),
    (4, 'HighTask2', '{}'::jsonb, '{}'::jsonb, 'in_progress'),
    (5, 'HighTask2', '{}'::jsonb, '{}'::jsonb, 'in_progress'),

    (6, 'HighTask2', '{}'::jsonb, '{}'::jsonb, 'in_progress'),
    (7, 'HighTask1', '{}'::jsonb, '{}'::jsonb, 'in_progress'),
    (8, 'MiddleTask8', '{}'::jsonb, '{}'::jsonb, 'in_progress'),
    (9, 'MiddleTask9', '{}'::jsonb, '{}'::jsonb, 'in_progress'),
    (10, 'MiddleTask10', '{}'::jsonb, '{}'::jsonb, 'in_progress'),

    (11, 'MiddleTask11', '{}'::jsonb, '{}'::jsonb, 'in_progress'),
    (12, 'MiddleTask12', '{}'::jsonb, '{}'::jsonb, 'in_progress'),
    (13, 'LowTask1', '{}'::jsonb, '{}'::jsonb, 'in_progress'),
    (14, 'LowTask2', '{}'::jsonb, '{}'::jsonb, 'in_progress'),
    (15, 'LowTask3', '{}'::jsonb, '{}'::jsonb, 'in_progress'),

    (16, 'LowTask1', '{}'::jsonb, '{}'::jsonb, 'in_progress'),
    (17, 'LowTask2', '{}'::jsonb, '{}'::jsonb, 'in_progress')
;
