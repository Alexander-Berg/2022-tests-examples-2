insert into clownductor.namespaces (name) values ('taxi');

INSERT INTO clownductor.projects
    (id, name, yp_quota_abc, network_stable, network_testing, tvm_root_abc, service_abc, namespace_id)
VALUES (1, 'taxi', 'a', 'a', 'a', 'a', 'a', 1)
;

INSERT INTO clownductor.services (id, name, project_id, artifact_name, cluster_type)
VALUES (1, 'clownductor', 1, 'a', 'nanny')
;

INSERT INTO task_manager.jobs (service_id, name, initiator, status)
VALUES (1, 'A', 'a', 'in_progress')
;
