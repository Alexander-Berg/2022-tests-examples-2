INSERT INTO balancers.namespaces (id, project_id, awacs_namespace, env, abc_quota_source)
VALUES (1, 1, 'test.net', 'stable', 'aaa'),
       (2, 1, 'test-2.net', 'stable', 'aab'),
       (3, 1, 'test-3.net', 'stable', 'aac')
;

INSERT INTO balancers.entry_points (id, namespace_id, awacs_upstream_id, protocol, dns_name, env)
VALUES (1, 1, 'default', 'http', 'test.net', 'stable'),
       (2, 2, 'default', 'http', 'test2.net', 'stable'),
       (3, 2, 'custom', 'http', 'test2.net', 'stable')
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
