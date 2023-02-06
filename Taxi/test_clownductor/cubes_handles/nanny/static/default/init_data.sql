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
    'test_service',
    'taxi/test_service/$',
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
    'testing',
    'testing',
    'test_service_testing'
), (
    1,
    'stable',
    'stable',
    'test_service_stable'
), (
    1,
    'pre_stable',
    'prestable',
    'test_service_pre_stable'
)
;

insert into permissions.roles (role, login, project_id, service_id, is_super)
values
    ('nanny_admin_prod', 'karachevda', null, null, true)
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
        'nanny', 1, null,
        '{"reallocation_settings": {"max_unavailable_pods_percent": 45, "min_update_delay_seconds": 350}}'::jsonb,
        '{"reallocation_settings": {"max_unavailable_pods_percent": 45, "min_update_delay_seconds": 350}}'::jsonb
    );


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
    'SyncServiceRemoteParameters',
    'elrusso',
    'in_progress'
);
