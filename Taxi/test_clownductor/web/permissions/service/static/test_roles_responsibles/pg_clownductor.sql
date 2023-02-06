insert into clownductor.namespaces (name) values ('taxi'), ('eda'), ('lavka');

insert into
    clownductor.projects (id, name, yp_quota_abc, network_stable, network_testing, tvm_root_abc, service_abc, namespace_id)
values
    (1, 'taxi', 'a', 'a', 'a', 'a', 'a', 1),
    (2, 'eda', 'b', 'b', 'b', 'b', 'b', 2),
    (3, 'lavka', 'b', 'b', 'b', 'b', 'b', 3)
;

insert into
    clownductor.services (id, name, project_id, artifact_name, cluster_type)
values
    (1, 'clownductor', 1, 'a', 'nanny'),
    (2, 'clownductor', 1, 'b', 'postgres'),
    (3, 'clownductor', 1, 'b', 'conductor'),

    (4, 'clownductor', 2, 'a', 'nanny'),
    (5, 'clownductor', 2, 'b', 'postgres'),
    (6, 'clownductor', 2, 'b', 'conductor'),

    (7, 'clownductor', 3, 'a', 'nanny'),
    (8, 'clownductor', 3, 'b', 'postgres'),
    (9, 'clownductor', 3, 'b', 'conductor'),

    (10, 'test_service_1', 1, 'b', 'nanny'),

    (11, 'test_service_2', 2, 'b', 'conductor'),

    (12, 'test_service_3', 3, 'a', 'nanny')
;

insert into
    permissions.roles (id, role, login, project_id, service_id, is_super)
values
    (1, 'nanny_admin_prod', 'super', null, null, true),
    (2, 'strongbox_secrets_prod', 'super', null, null, true),

    (3, 'granded', 'super', 1, null, false),

    (4, 'deploy_approve_manager', 'login2', 2, null, false),
    (5, 'nanny_admin_testing', 'login2', 2, null, false),

    (6, 'nanny_admin_prod', 'login3', 3, null, false),
    (7, 'strongbox_secrets_prod', 'login3', 3, null, false),

    (8, 'deploy_approve_manager', 'login4', null, 1, false),
    (9, 'nanny_admin_testing', 'login4', null, 1, false),
    (10, 'strongbox_secrets_testing', 'login4', null, 1, false),

    (11, 'deploy_approve_manager', 'login5', null, 11, false),
    (12, 'nanny_admin_testing', 'login5', null, 4, false),

    (13, 'deploy_approve_manager', 'login1', 1, null, false),
    (14, 'nanny_admin_testing', 'login1', 1, null, false),
    (15, 'strongbox_secrets_testing', 'login1', 1, null, false),

    (16, 'nanny_admin_prod', 'login6', null, 7, false),
    (17, 'strongbox_secrets_prod', 'login6', null, 7, false)
;
