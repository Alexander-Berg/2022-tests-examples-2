INSERT INTO balancers.namespaces (project_id, awacs_namespace, env, abc_quota_source, is_external)
VALUES (1, 'ns1', 'stable', 'abcstable', true),
       (1, 'ns2', 'testing', 'abctesting', false),
       (2, 'ns3', 'stable', 'abcstable', false)
;

INSERT INTO balancers.entry_points
    (id, namespace_id, awacs_upstream_id, protocol, dns_name, env, routing_mode)
VALUES (1, 1, 'ns1', 'http', 'fqdn.net', 'stable', 'round-robin'),
       (2, 2, 'ns2', 'http', 'fqdn.test.net', 'testing', 'dc-local'),
       (3, 3, 'ns3', 'https', 'fqdn2.net', 'stable', 'dc-local')
;

INSERT INTO balancers.upstreams (id, branch_id, service_id, awacs_backend_id, env)
VALUES (1, 1, 1, 'backend1', 'stable'),
       (2, 2, 1, 'backend2', 'prestable'),
       (3, 3, 1, 'backend3', 'testing'),
       (4, 4, 2, 'backend4', 'stable')
;

INSERT INTO balancers.entry_points_upstreams (entry_point_id, upstream_id)
VALUES (1, 1),
       (1, 2),
       (2, 3),
       (3, 4)
;
