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
), (
    'test_eda_project',
    '_EDATESTNETS_',
    '_HWEDANETS_',
    'edaservicesdeploymanagement',
    'edaquotaypdefault',
    'edatvmaccess',
    2
)
;

insert into clownductor.services (
    project_id,
    name,
    artifact_name,
    cluster_type,
    requester,
    abc_service,
    service_url,
    direct_link
)
values (
    1,
    'test_service',
    'taxi/test_service/$',
    'nanny',
    'unit_test',
    'abc_service',
    'https://github.yandex-team.ru/taxi/uservices/blob/develop/services/test_service/service.yaml',
    'taxi_test_service'
), (
    1,
    'test_service_2',
    'taxi/test_service_2/$',
    'nanny',
    'unit_test',
    'abc_service',
    'https://github.yandex-team.ru/taxi/uservices/blob/develop/services/test_service/service.yaml',
    'taxi_test_service_2'
), (
    1,
    'test_service_3',
    'taxi/test_service_3/$',
    'nanny',
    'unit_test',
    'abc_service',
    'https://github.yandex-team.ru/taxi/uservices/blob/develop/services/test_service/service.yaml',
    'taxi_test_service_3'
), (
    1,
    'test_service_4',
    'taxi/test_service_4/$',
    'nanny',
    'unit_test',
    'abc_service',
    null,
    'taxi_test_service_4'
), (
    2,
    'test_service_4',
    'taxi/test_service_4/$',
    'nanny',
    'unit_test',
    'abc_service',
    null,
    'taxi_test_service_4'
), (
    1,
    'test_service_5',
    'taxi/test_service_5/$',
    'nanny',
    'unit_test',
    'abc_service',
    null,
    'taxi_test_service_5'
), (
    2,
    'test_service_5',
    'taxi/test_service_5/$',
    'nanny',
    'unit_test',
    'abc_service',
    null,
    'taxi_test_service_5'
), (
    1,
    'test_service_rollback',
    'taxi/test_service_rollback/$',
    'nanny',
    'unit_test',
    'abc_service',
    null,
    'taxi_test_service_rollback'
), (
    1,
    'test_service_9',
    'taxi/test_service_9/$',
    'nanny',
    'unit_test',
    'abc_service',
    'https://github.yandex-team.ru/taxi/uservices/blob/develop/services/test_service/service.yaml',
    'taxi_test_service_9'
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
), (
    1,
    'stable',
    'stable',
    'test_service_stable'
), (
    2,
    'unstable',
    'unstable',
    'test_service_2_unstable'
), (
    2,
    'stable',
    'stable',
    'test_service_2_stable'
), (
    3,
    'unstable',
    'unstable',
    'test_service_3_unstable'
), (
    3,
    'stable',
    'stable',
    'test_service_3_stable'
), (
    1,
    'prestable',
    'prestable',
    'test_service_pre_stable'
), (
    2,
    'prestable',
    'prestable',
    'test_service_2_pre_stable'
), (
    3,
    'prestable',
    'prestable',
    'test_service_3_pre_stable'
), (
    4,
    'stable',
    'stable',
    'test_project_service_4_stable'
), (
    4,
    'prestable',
    'prestable',
    'test_project_service_pre_4_stable'
), (
    5,
    'stable',
    'stable',
    'test_eda_project_service_4_stable'
), (
    5,
    'prestable',
    'prestable',
    'test_eda_project_service_pre_4_stable'
), (
    6,
    'stable',
    'stable',
    'test_project_service_5_stable'
), (
    6,
    'prestable',
    'prestable',
    'test_project_service_pre_5_stable'
), (
    7,
    'stable',
    'stable',
    'test_eda_project_service_5_stable'
), (
    7,
    'prestable',
    'prestable',
    'test_eda_project_service_pre_5_stable'
), (
    8,
    'stable',
    'stable',
    'test_taxi_project_service_rollback_stable'
), (
    8,
    'prestable',
    'prestable',
    'test_taxi_project_service_rollback_pre_stable'
), (
    9,
    'unstable',
    'unstable',
    'test_block_diff_unstable'
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
    'DeployNannyServiceWithApprove',
    'karachevda',
    'in_progress'
), (
    1,
    3,
    'DeployNannyServiceNoApprove',
    'deoevgen',
    'in_progress'
)
;

alter sequence task_manager.jobs_id_seq restart with 1000;
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
    3,
    6,
    'ResolveServiceDiff',
    'deoevgen',
    'in_progress',
    1,
    '3_6_ResolveServiceDiff',
    '3_6_ResolveServiceDiff'
),(
    8,
    18,
    'DeployNannyServiceWithApprove',
    'karachevda',
    'success', 1,
    '1_2_DeployNannyServiceWithApprove',
    '1_2_DeployNannyServiceWithApprove'
), (
    9,
    20,
    'ResolveServiceDiff',
    'azhuchkov',
    'in_progress',
    1,
    '9_20_ResolveServiceDiff',
    '9_20_ResolveServiceDiff'
)
;
alter sequence task_manager.jobs_id_seq restart with 4;

insert into
    task_manager.job_variables (
    job_id,
    variables
)
values (
    1,
    '{"name": "DeployNannyServiceWithApprove", "image": "taxi/test_service/production:0.1.1", "comment": "test comment", "sandbox_resources": null}'
), (
    2,
    '{"name": "DeployNannyServiceNoApprove", "image": "taxi/test_service/unstable:0.1.3unstable295", "comment": "test comment", "release_ticket_st": "TAXIREL-13", "sandbox_resources": null}'
), (
    3,
    '{"name": "DeployNannyServiceNoApprove", "image": "taxi/test_service/testing:0.1.2testing21", "comment": "test comment", "sandbox_resources": null}'
), (
    1001,
    '{"name": "DeployNannyServiceWithApprove", "image": "taxi/test_service_rollback/production:0.2.0", "comment": "test comment", "sandbox_resources": null}'
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
    ),
    (
        'nanny', 2, 4,
        '{"cpu": 1000}'::jsonb,
        '{"cpu": 2000}'::jsonb
    ),
    (
        'nanny', 3, 6,
        '{"cpu": 1000}'::jsonb,
        '{"cpu": 500}'::jsonb
    ),
    (
        'nanny', 9, 20,
        '{"cpu": 1000}'::jsonb,
        '{"cpu": 500}'::jsonb
    ),
    (
        'service_info', 1, 2,
        '{"duty": {"abc_slug": "service4", "primary_schedule": "primaryschedule"}}'::jsonb,
        '{"duty": {"abc_slug": "service4", "primary_schedule": "primaryschedule"}}'::jsonb
    );

insert into clownductor.related_services (
    service_id,
    related_service_id,
    relation_type
)
values (
    2, 1, 'alias_main_service'
),(
    3, 1, 'alias_main_service'
),(
    5, 4, 'alias_main_service'
),(
    6, 4, 'alias_main_service'
),(
    7, 4, 'alias_main_service'
)
;
