insert into clownductor.namespaces (name) values ('taxi');

insert into
    clownductor.projects (
        name,
        network_testing,
        network_stable,
        service_abc,
        yp_quota_abc,
        tvm_root_abc,
        owners,
        namespace_id
    )
values (
    'test_project',
    '_taxitestnets_',
    '_hwtaxinets_',
    'taxiservicesdeploymanagement',
    'taxiquotaypdefault',
    'taxitvmaccess',
    '{"groups": ["special_admin_group"], "logins": ["special_admin_login"]}'::jsonb,
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
    'test-service-direct'
), (
    1,
    'testing_branch',
    'testing',
    'test-service-direct-testing'
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
    ('service_info', 1, 1, '{"duty_group_id": "1b69be79c5755f678048a169"}'::jsonb, '{"duty_group_id": "1b69be79c5755f678048a169"}'::jsonb),
    ('nanny', 1, 1, '{"cpu": 1000}'::jsonb, '{"cpu": 1000}'::jsonb),
    ('nanny', 1, 2, '{"cpu": 1000}'::jsonb, '{"cpu": 1000}'::jsonb),
    ('abc', 1, 1, '{"maintainers": ["vokhcuhz", "test_maintainer"]}'::jsonb, '{}'::jsonb)
;

INSERT INTO permissions.roles (login, role, service_id, project_id, is_super)
VALUES ('azhuchkov-super-testing', 'nanny_admin_testing', NULL, NULL, TRUE),
       ('azhuchkov-super-stable', 'nanny_admin_prod', NULL, NULL, TRUE),
       ('azhuchkov-srv-testing', 'nanny_admin_testing', 1, NULL, FALSE),
       ('azhuchkov-srv-stable', 'nanny_admin_prod', 1, NULL, FALSE),
       ('azhuchkov-prj-testing', 'nanny_admin_testing', NULL, 1, FALSE),
       ('azhuchkov-prj-stable', 'nanny_admin_prod', NULL, 1, FALSE)
;
