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
), (
    1,
    'test-service-3',
    'artifact_name_3',
    'conductor',
    'unit_test',
    'abc_service_3'
), (
    1,
    'test-service-4',
    'artifact_name_4',
    'nanny',
    'unit_test',
    'abc_service_4'
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
    2,
    'stable_branch',
    'stable',
    'test-service-2-direct'
), (
    3,
    'stable_branch',
    'stable',
    'test-service-3-direct'
), (
    1,
    'pre_stable_branch',
    'prestable',
    'test-service-pre-1-direct'
)
;


insert into task_manager.jobs (
    service_id,
    branch_id,
    name,
    initiator,
    status,
    created_at,
    idempotency_token,
    change_doc_id
)
values (
    1,
    1,
    'NOTSyncServiceRemoteParameters',
    'karachevda',
    'canceled',
    1600000000,
    null,
    null
), (
    1,
    1,
    'NOTSyncServiceRemoteParameters',
    'karachevda',
    'canceled',
    1600000000,
    null,
    null
), (
    1,
    1,
    'SyncServiceRemoteParameters',
    'karachevda',
    'canceled',
    1600000000,
    null,
    null
), (
    1,
    1,
    'SyncServiceRemoteParameters',
    'karachevda',
    'canceled',
    1600000000,
    null,
    null
), (
    1,
    1,
    'SyncServiceRemoteParameters',
    'karachevda',
    'canceled',
    1600000000,
    null,
    null
), (
    1,
    1,
    'SyncServiceRemoteParameters',
    'karachevda',
    'canceled',
    1600000000,
    null,
    null
), (
    1,
    1,
    'SyncServiceRemoteParameters',
    'karachevda',
    'canceled',
    1600000000,
    null,
    null
), (
    2,
    3,
    'SyncServiceRemoteParameters',
    'karachevda',
    'canceled',
    1600000000,
    null,
    null
), (
    2,
    3,
    'SyncServiceRemoteParameters',
    'karachevda',
    'canceled',
    1600000000,
    null,
    null
), (
    2,
    3,
    'SyncServiceRemoteParameters',
    'karachevda',
    'canceled',
    1600000000,
    null,
    null
), (
    2,
    3,
    'SyncServiceRemoteParameters',
    'karachevda',
    'canceled',
    1600000000,
    null,
    null
), (
    2,
    3,
    'SyncServiceRemoteParameters',
    'karachevda',
    'in_progress',
    1600000000,
    '2_3_SyncServiceRemoteParameters',
    '2_3_SyncServiceRemoteParameters'
), (
    1,
    1,
    'SyncServiceRemoteParameters',
    'karachevda',
    'in_progress',
    1606000000,
    '1_1_SyncServiceRemoteParameters',
    '1_1_SyncServiceRemoteParameters'
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
    (7, '{}'),
    (8, '{}'),
    (9, '{}'),
    (10, '{}'),
    (11, '{}'),
    (12, '{}'),
    (13, '{}')
;

