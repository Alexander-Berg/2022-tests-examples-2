INSERT INTO balancers.namespaces (id, project_id, awacs_namespace, env, abc_quota_source)
VALUES  (2, 1, 'ns1', 'stable', 'abcstable'),
        (10, 2, 'temp1', 'stable', 'infostable'),
        (11, 2, 'temp2', 'testing', 'infostable')
;

INSERT INTO balancers.entry_points
    (id, namespace_id, awacs_upstream_id, protocol, dns_name, env)
VALUES (2, 2, 'ns1', 'http', 'fqdn.net', 'stable'),
       (3, 10, 'ns2', 'http', 'fqdn.net', 'stable'),
       (4, 11, 'ns3', 'http', 'fqdn.net', 'stable')
;

INSERT INTO balancers.upstreams (id, branch_id, service_id, awacs_backend_id, env)
VALUES (3, 3, 1, 'backend1', 'stable'),
       (4, 4, 1, 'backend2', 'prestable'),
       (5, 6, 2, 'backend3', 'prestable')
;

INSERT INTO balancers.entry_points_upstreams (entry_point_id, upstream_id)
VALUES (2, 3),
       (2, 4),
       (3, 5)
;
