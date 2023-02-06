INSERT INTO balancers.namespaces (project_id, awacs_namespace, env, abc_quota_source)
VALUES (1, 'ns1', 'stable', 'abcstable'),
       (1, 'ns2', 'testing', 'abctesting')
;

INSERT INTO balancers.entry_points
    (id, namespace_id, awacs_upstream_id, protocol, dns_name, env)
VALUES (1, 1, 'ns1', 'http', 'fqdn.net', 'stable'),
       (2, 2, 'ns2', 'http', 'fqdn.test.net', 'testing')
;

INSERT INTO balancers.upstreams (id, branch_id, service_id, awacs_backend_id, env)
VALUES (1, 1, 1, 'backend1', 'stable'),
       (2, 2, 1, 'backend2', 'prestable'),
       (3, 3, 1, 'backend3', 'testing')
;

INSERT INTO balancers.entry_points_upstreams (entry_point_id, upstream_id)
VALUES (1, 1),
       (1, 2),
       (2, 3)
;
