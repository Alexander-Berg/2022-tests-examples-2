INSERT INTO balancers.namespaces (id, project_id, awacs_namespace, env, abc_quota_source)
VALUES (1, 1, 'test.net', 'stable', 'aaa'),
       (2, 1, 'test-2.net', 'stable', 'aab'),
       (3, 1, 'test-3.net', 'stable', 'aac'),
       (4, 1, 'test-4.net', 'stable', 'aad')
;
INSERT INTO balancers.namespaces (id, project_id, awacs_namespace, env, abc_quota_source, is_shared, is_external)
VALUES (5, 1, 'test-5.net', 'stable', 'aaa', True, False),
       (6, 1, 'test-6.net', 'stable', 'aaa', False, True)
;

INSERT INTO balancers.entry_points (id, namespace_id, awacs_upstream_id, protocol, dns_name, env)
VALUES (1, 1, 'default', 'http', 'test.net', 'stable'),
       (2, 2, 'default', 'http', 'test2.net', 'stable'),
       (3, 3, 'default', 'http', 'test3.net', 'stable'),
       (4, 6, 'default', 'https', 'test6.net', 'stable')
;

INSERT INTO balancers.upstreams (id, branch_id, service_id, awacs_backend_id, env)
VALUES (1, 1, 1, 'some', 'stable'),
       (2, 2, 1, 'some', 'prestable')
;

INSERT INTO balancers.entry_points_upstreams (entry_point_id, upstream_id)
VALUES (1, 1),
       (1, 2),
       (2, 1)
;
ALTER SEQUENCE balancers.entry_points_id_seq RESTART WITH 10;
ALTER SEQUENCE balancers.entry_points_upstreams_id_seq RESTART WITH 10;
