insert into clownductor.namespaces (name) values ('taxi');

INSERT INTO clownductor.projects (
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

INSERT INTO clownductor.services (
    project_id,
    name,
    artifact_name,
    cluster_type,
    requester,
    abc_service,
    service_url
)
VALUES (
    1,
    'test_service',
    'taxi/test_service/$',
    'nanny',
    'unit_test',
    'abc_service',
    'https://github.yandex-team.ru/taxi/uservices/blob/develop/services/test_service/service.yaml'
)
;

insert into task_manager.jobs (
    id,
    service_id,
    name,
    initiator,
    status,
    created_at,
    finished_at,
    real_time,
    total_time
)
values (
    1,
    1,
    'job1',
    '',
    'success',
    EXTRACT(EPOCH FROM NOW() - INTERVAL '12 MINUTES'),
    EXTRACT(EPOCH FROM NOW() - INTERVAL '11 MINUTES'),
    1,
    1
)
;

insert into task_manager.tasks (
    id,
    job_id,
    name,
    input_mapping,
    output_mapping,
    status,
    created_at,
    updated_at,
    real_time,
    total_time
)
values (
    1,
    1,
    'task1',
    '',
    '',
    'success'::JOB_STATUS,
    EXTRACT(EPOCH FROM NOW() - INTERVAL '12 MINUTES'),
    EXTRACT(EPOCH FROM NOW() - INTERVAL '11 MINUTES'),
    1,
    1
),
(
    2,
    1,
    'task2',
    '',
    '',
    'success'::JOB_STATUS,
    EXTRACT(EPOCH FROM NOW() - INTERVAL '12 MINUTES'),
    EXTRACT(EPOCH FROM NOW() - INTERVAL '10 MINUTES 20 SECONDS'),
    1,
    1
)
;

INSERT INTO task_manager.task_deps VALUES (1, 2);
