INSERT INTO balancers.namespaces
    (id, project_id, awacs_namespace, env, abc_quota_source, is_shared, is_external, created_at, updated_at)
VALUES (1, 1, 'aaa.net', 'stable', 'some', FALSE, FALSE, '2020-06-05T12:00:00Z', '2020-06-05T12:10:00Z'),
       (2, 1, 'bbb.net', 'stable', 'some', FALSE, TRUE, '2020-06-05T12:00:00Z', '2020-06-05T12:10:00Z'),
       (3, 1, 'ccc.net', 'stable', 'some', FALSE, FALSE, '2020-06-05T12:00:00Z', '2020-06-05T12:10:00Z'),
       (4, 1, 'ddd.net', 'stable', 'some', TRUE, FALSE, '2020-06-05T12:00:00Z', '2020-06-05T12:10:00Z'),
       (5, 1, 'eee.net', 'stable', 'some', FALSE, FALSE, '2020-06-05T12:00:00Z', '2020-06-05T12:10:00Z')
;

INSERT INTO balancers.entry_points (id, namespace_id, protocol, dns_name, env, awacs_upstream_id, is_external)
VALUES (1, 1, 'http'::balancers.entry_point_protocol_t, 'test.net', 'stable'::balancers.entry_point_env_t, 'aaa', FALSE),
       (2, 2, 'https'::balancers.entry_point_protocol_t, 'ext-test.net', 'stable'::balancers.entry_point_env_t, 'bbb', TRUE),
       (3, 4, 'http'::balancers.entry_point_protocol_t, 'more-test.net', 'stable'::balancers.entry_point_env_t, 'ccc', FALSE),
       (15, 5, 'http'::balancers.entry_point_protocol_t, 'one-more.net', 'stable'::balancers.entry_point_env_t, 'eee', FALSE)
;

INSERT INTO balancers.upstreams (id, branch_id, service_id, awacs_backend_id, env)
VALUES (1, 1, 1, 'aaa', 'stable'::balancers.upstream_env_t),
       (2, 2, 1, 'aaa', 'prestable'::balancers.upstream_env_t),
       (3, 4, 2, 'bbb', 'prestable'::balancers.upstream_env_t)
;

INSERT INTO balancers.entry_points_upstreams (entry_point_id, upstream_id)
VALUES (1, 1),
       (1, 2),
       (2, 1),
       (2, 2),
       (15, 3)
;
