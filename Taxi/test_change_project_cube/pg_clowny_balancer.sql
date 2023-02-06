
INSERT INTO balancers.namespaces
    (project_id, awacs_namespace, env, abc_quota_source, is_shared, is_external)
VALUES  (1, 'aaa.net',     'stable', 'some', FALSE, FALSE),
        (1, 'aaa.tst.net', 'testing', 'some', FALSE, FALSE),
        (1, 'aaabbb.tst.net', 'testing', 'some', FALSE, FALSE),
        (1, 'aaabbb.2tst.net', 'testing', 'some', FALSE, FALSE),
        (3, 'aaabbb.22tst.net', 'testing', 'some', FALSE, FALSE);

INSERT INTO balancers.entry_points (namespace_id, protocol, dns_name, env, awacs_upstream_id, is_external)
VALUES  (1, 'http'::balancers.entry_point_protocol_t, 'test.net', 'stable'::balancers.entry_point_env_t, 'aaa', FALSE),
        (2, 'http'::balancers.entry_point_protocol_t, 'test.tst.net', 'testing'::balancers.entry_point_env_t, 'aaa', FALSE),
        (5, 'http'::balancers.entry_point_protocol_t, 'test2.tst.net', 'testing'::balancers.entry_point_env_t, 'aaab', FALSE);

INSERT INTO balancers.upstreams (branch_id, service_id, awacs_backend_id, env)
VALUES  (1, 1, 'aaa', 'stable'::balancers.upstream_env_t),
        (2, 2, 'aaa.tst', 'stable'::balancers.upstream_env_t);

INSERT INTO balancers.entry_points_upstreams (entry_point_id, upstream_id)
VALUES (1, 1),
       (2, 1),
       (3, 2);
