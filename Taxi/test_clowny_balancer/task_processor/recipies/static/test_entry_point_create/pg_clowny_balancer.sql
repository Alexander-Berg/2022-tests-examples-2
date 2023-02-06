INSERT INTO balancers.namespaces
    (id, project_id, awacs_namespace, env, abc_quota_source, is_shared, is_external, created_at, updated_at)
VALUES (3, 1, 'ns_1', 'stable', 'some', FALSE, FALSE, '2020-06-05T12:00:00Z', '2020-06-05T12:10:00Z'),
       (4, 1, 'ns_2', 'stable', 'some', TRUE, FALSE, '2020-06-05T12:00:00Z', '2020-06-05T12:10:00Z')
;

INSERT INTO balancers.entry_points (id, namespace_id, protocol, dns_name, env, awacs_upstream_id, is_external)
VALUES (3, 4, 'http'::balancers.entry_point_protocol_t, 'more-test.net', 'stable'::balancers.entry_point_env_t, 'ccc', FALSE)
;

INSERT INTO balancers.upstreams (id, branch_id, service_id, awacs_backend_id, env)
VALUES (2, 1, 1, 'aaa', 'stable'::balancers.upstream_env_t),
       (3, 4, 2, 'bbb', 'stable'::balancers.upstream_env_t)
;

INSERT INTO balancers.entry_points_upstreams (entry_point_id, upstream_id)
VALUES (3, 2)
;
