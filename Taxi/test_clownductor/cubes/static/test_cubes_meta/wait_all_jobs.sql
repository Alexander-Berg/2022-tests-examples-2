insert into clownductor.namespaces (name) values ('taxi');

INSERT INTO clownductor.projects (name, network_testing, network_stable, service_abc, yp_quota_abc, tvm_root_abc, namespace_id)
VALUES ('test-project', 'TESTING', 'STABLE', 'abctestproject', 'abctestproject', 'abctestproject', 1);

INSERT INTO clownductor.services (project_id, name, artifact_name, cluster_type)
VALUES (1, 'test-service', '', 'nanny');

INSERT INTO clownductor.branches (service_id, name, direct_link)
VALUES (1, 'test-branch', '');

INSERT INTO task_manager.jobs
    (service_id, branch_id, name, status, remote_job_id)
VALUES (1, 1, 'cool_job',  'success', 1),
       (1, 1, 'cool_job', 'success', 2),
       (1, 1, 'cool_job', 'success', 3),
       (1, 1, 'cool_job', 'success', 4);
