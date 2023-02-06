insert into clownductor.namespaces (name) values ('test');

INSERT INTO clownductor.projects (id, name, network_testing, network_stable, service_abc, yp_quota_abc, tvm_root_abc, env_params, namespace_id)
VALUES (1, 'test', '', '', '', '', '', '{"unstable": {"domain": "yataxi.net"}}'::jsonb, 1);

INSERT INTO clownductor.services
    (id, project_id, name, artifact_name, cluster_type, wiki_path, abc_service, tvm_stable_abc_service, tvm_testing_abc_service)
VALUES (1, 1, 'test-service', '', 'nanny', '', '', '', '');

INSERT INTO clownductor.branches (id, service_id, name, env, direct_link)
VALUES
       (1, 1, 'test-branch-unstable', 'unstable', 'test_branch_unstable'),
       (2, 1, 'test-branch-testing', 'testing', 'test_branch_testing');

INSERT INTO clownductor.hosts (name, branch_id, datacenter)
VALUES
       ('test-fqdn', 1, 'man'),
       ('test-fqdn-t', 2, 'man');
