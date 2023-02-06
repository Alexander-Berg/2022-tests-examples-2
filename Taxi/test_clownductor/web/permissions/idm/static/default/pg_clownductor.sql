insert into clownductor.namespaces (name) values ('taxi'), ('eda');

INSERT INTO clownductor.projects
    (id, name, yp_quota_abc, network_stable, network_testing, tvm_root_abc, service_abc, namespace_id)
VALUES (1, 'taxi', 'a', 'a', 'a', 'a', 'a', 1),
       (2, 'eda', 'b', 'b', 'b', 'b', 'b', 2);
INSERT INTO clownductor.projects
    (id, name, yp_quota_abc, network_stable, network_testing, tvm_root_abc, service_abc, namespace_id, deleted_at)
VALUES (3, 'taxi-deleted', 'a', 'a', 'a', 'a', 'a', 1, 123);

INSERT INTO clownductor.services (id, name, project_id, artifact_name, cluster_type)
VALUES (1, 'clownductor', 1, 'a', 'nanny'),
       (2, 'clownductor', 1, 'b', 'postgres');

INSERT INTO permissions.roles (role, login, project_id, service_id, is_super)
VALUES ('deploy_approve_manager', 'd1mbas', 1, NULL, FALSE);
