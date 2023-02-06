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
    'test-service',
    'artifact_name',
    'nanny',
    'unit_test',
    'abc_service'
), (
    1,
    'test-service-2',
    'artifact_name_2',
    'nanny',
    'unit_test',
    'abc_service_2'
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
), (
    1,
    'testing_branch',
    'testing',
    'test-service-1-direct-testing'
), (
    1,
    'tank',
    'testing',
    'tank-expired-1'
), (
    2,
    'stable_branch',
    'stable',
    'test-service-2-direct'
), (
    2,
    'testing_branch',
    'testing',
    'test-service-2-direct-testing'
), (
    2,
    'tank',
    'testing',
    'tank-expired-2'
), (
    2,
    'tank-not-expired',
    'testing',
    'tank-not-expired'
)
;


insert into task_manager.jobs (
    service_id,
    branch_id,
    name,
    initiator,
    status,
    finished_at
)
values (
    1,
    1,
    'CreateFullNannyBranch',
    'karachevda',
    'success',
    1505538527
), (
    1,
    2,
    'CreateFullNannyBranch',
    'karachevda',
    'success',
    1604948400
), (
    1,
    3,
    'CreateFullNannyBranch',
    'karachevda',
    'success',
    1604948400
), (
    2,
    4,
    'CreateFullNannyBranch',
    'karachevda',
    'success',
    1604948400
), (
    2,
    5,
    'CreateFullNannyBranch',
    'karachevda',
    'success',
    1604948400
), (
    2,
    6,
    'CreateFullNannyBranch',
    'karachevda',
    'success',
    1604948400
), (
    2,
    7,
    'CreateFullNannyBranch',
    'karachevda',
    'success',
    1605538527
)
;

insert into
    task_manager.job_variables (
        job_id,
        variables
    )
values
    (1, '{}'),
    (2, '{}'),
    (3, '{}'),
    (4, '{}'),
    (5, '{}'),
    (6, '{}'),
    (7, '{}')
;

