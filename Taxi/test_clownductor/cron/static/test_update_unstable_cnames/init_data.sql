INSERT INTO clownductor.namespaces (name) values ('taxi');

INSERT INTO clownductor.projects (id, name, network_testing, network_stable, service_abc, yp_quota_abc, tvm_root_abc, env_params, namespace_id)
VALUES (1, 'test', '', '', '', '', '', '{"unstable": {"domain": "yataxi.net"}}'::jsonb, 1);

INSERT INTO clownductor.services
    (id, project_id, name, artifact_name, cluster_type, wiki_path, abc_service, tvm_stable_abc_service, tvm_testing_abc_service)
VALUES (1, 1, 'test-service', '', 'nanny', '', '', '', '');

INSERT INTO clownductor.branches (id, service_id, name, env, direct_link, deleted_at)
VALUES
       (1, 1, 'test-branch-unstable', 'unstable', 'test_branch_unstable', null),
       (2, 1, 'test-branch-testing', 'testing', 'test_branch_testing', null),
       (3, 1, 'test-branch-unstable-deleted', 'unstable', 'test_branch_unstable', 123),
       (4, 1, 'unstable-branch-with-ep', 'unstable', 'unstable_branch_with_ep', null);

INSERT INTO clownductor.hosts (name, branch_id, datacenter)
VALUES
       ('test-fqdn', 1, 'man'),
       ('test-fqdn-d', 3, 'man'),
       ('test-fqdn-t', 2, 'man'),
       ('test-fqdn-4', 4, 'man');
