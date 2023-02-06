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
    '{"groups": ["special_admin_group"], "logins": ["project_login_11"]}'::jsonb,
    1
), (
    'test_project_2',
    '_taxitestnets2_',
    '_hwtaxinets2_',
    'taxiservicesdeploymanagement2',
    'taxiquotaypdefault2',
    'taxitvmaccess2',
    '{"groups": ["special_admin_group"], "logins": ["project_login_21", "project_login_22"]}'::jsonb,
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
    2,
    'test-service-2',
    'artifact_name_2',
    'nanny',
    'unit_test',
    'abc_service_2'
), (
    2,
    'test-service-3',
    'artifact_name_3',
    'nanny',
    'unit_test',
    'abc_service_3'
), (
    2,
    'test_service_2',
    'artifact_name_3',
    'postgres',
    'unit_test',
    'abc_service_pg'
), (
    2,
    'test-service-4',
    'artifact_name_4',
    'nanny',
    'unit_test',
    'abc_service_4'
), (
    2,
    'test-service-5',
    'artifact_name_5',
    'nanny',
    'unit_test',
    'abc_service_5'
),(
    2,
    'test_service_2_mongo',
    'artifact_name_6',
    'mongo_mdb',
    'unit_test',
    'abc_service_mongo'
),(
    2,
    'test_service_2_redis',
    'artifact_name_7',
    'redis_mdb',
    'unit_test',
    'abc_service_redis'
),(
    2,
    'test_service_2_clickhouse',
    'artifact_name_8',
    'clickhouse',
    'unit_test',
    'abc_service_clickhouse'
),(
    2,
    'test_service_2_mysql',
    'artifact_name_9',
    'mysql',
    'unit_test',
    'abc_service_mysql'
),(
    1,
    'test-service-11',
    'artifact_name_11',
    'nanny',
    'unit_test',
    'abc_service_11'
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
    5,
    'stable_branch',
    'stable',
    'test-service-4-direct'
), (
    6,
    'stable',
    'stable',
    'test-service-5-direct'
), (
    11,
    'stable',
    'stable',
    'test-service-11-direct'
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
    ('abc', 1, 1, '{"maintainers": ["karachevda", "meow"]}'::jsonb, '{}'::jsonb),
    ('service_info', 2, 1, '{"duty_group_id": "2b69be79c5755f678048a169"}'::jsonb, '{"duty_group_id": "2b69be79c5755f678048a169"}'::jsonb),
    ('abc', 2, 3, '{"maintainers": ["test_maintainers_21", "test_maintainers_22"]}'::jsonb, '{"maintainers": ["karachevda"]}'::jsonb),
    ('service_info', 3, null, '{"service_name": "test-service-3"}'::jsonb, null),
    ('service_info', 5, null, '{"duty_group_id": "4b69be79c5755f678048a169"}'::jsonb, '{"duty_group_id": "4b69be79c5755f678048a169"}'::jsonb),
    ('service_info', 6, null, '{"service_name": "test-service-5", "duty_group_id": "bad"}'::jsonb, null),
    ('service_info', 11, 7, '{"duty": {"abc_slug": "abc_slug", "primary_schedule": "primary_schedule"}}'::jsonb, '{"duty": {"abc_slug": "abc_slug", "primary_schedule": "primary_schedule"}}'::jsonb)
;

INSERT INTO permissions.roles (login, role, service_id, project_id, is_super)
VALUES ('d1mbas-super', 'nanny_admin_testing', NULL, NULL, TRUE),
       ('d1mbas-service_1', 'nanny_admin_testing', 1, NULL, FALSE),
       ('d1mbas-project_1',' nanny_admin_testing', NULL, 1, FALSE),
       ('d1mbas-service_2', 'nanny_admin_testing', 2, NULL, FALSE),
       ('d1mbas-mdb', 'mdb_cluster_ro_access', NULL, 2, FALSE),
       ('d1mbas-mdb-super', 'mdb_cluster_ro_access', NULL, NULL, TRUE),
       ('some_admin', 'mdb_cluster_ro_access', NULL, NULL, TRUE),
       ('some-developer', 'nanny_developer', 1, NULL, FALSE),
       ('some-evicter', 'nanny_evicter', 1, NULL, FALSE)
;
