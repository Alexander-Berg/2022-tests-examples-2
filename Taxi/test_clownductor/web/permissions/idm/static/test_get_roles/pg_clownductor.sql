insert into clownductor.namespaces (name) values ('taxi');

INSERT INTO clownductor.projects
    (id, name, yp_quota_abc, network_stable, network_testing, tvm_root_abc, service_abc, namespace_id)
VALUES (1, 'taxi', 'a', 'a', 'a', 'a', 'a', 1);

INSERT INTO clownductor.services (id, name, project_id, artifact_name, cluster_type)
VALUES (2, 'clownductor', 1, 'a', 'nanny');

INSERT INTO permissions.roles (role, login, project_id, service_id, is_super)
VALUES ('deploy_approve_manager', 'd1mbas', 1, NULL, FALSE),
       ('deploy_approve_programmer', 'd1mbas', NULL, 2, FALSE),
       ('nanny_admin_prod', 'd1mbas', NULL, NULL, TRUE);


-- deleted project
INSERT INTO clownductor.projects
    (id, name, yp_quota_abc, network_stable, network_testing, tvm_root_abc, service_abc, namespace_id, deleted_at)
VALUES (2, 'eda', 'a', 'a', 'a', 'a', 'a', 1, 123);

INSERT INTO clownductor.services (id, name, project_id, artifact_name, cluster_type, deleted_at)
VALUES (3, 'clownductor', 1, 'a', 'nanny', 123),  -- deleted service in non deleted project
       (4, 'clownductor', 2, 'a', 'nanny', 123);  -- deleted service in deleted project

INSERT INTO permissions.roles (role, login, project_id, service_id, is_super)
VALUES ('deploy_approve_manager', 'd1mbas', 2, NULL, FALSE),  -- role in deleted project
       ('deploy_approve_programmer', 'd1mbas', NULL, 3, FALSE),  -- role in deleted service (from deleted project)
       ('deploy_approve_programmer', 'd1mbas', NULL, 4, FALSE);  -- role in deleted service (from non deleted project)
